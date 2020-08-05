import time
import json
import pytest

import pandas as pd
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import VectorAssembler

import bentoml
from tests.bento_service_examples.pyspark_classifier import PysparkClassifier
from tests.integration.api_server.conftest import _wait_until_ready

train_data = [[0, -1.0], [1, 1.0]]
train_pddf = pd.DataFrame(train_data, columns=["label", "feature1"])
test_data = [-5.0, 5.0, -0.5, 0.5]
test_pddf = pd.DataFrame(test_data, columns=["feature1"])


@pytest.fixture(scope="module")
def pyspark_model(spark_session):
    # Put pandas training df into Spark df form with Vector features
    train_spdf = spark_session.createDataFrame(train_pddf)
    assembler = VectorAssembler(inputCols=['feature1'], outputCol='features')
    train_spdf = assembler.transform(train_spdf).select(['features', 'label'])

    # Train model (should result in x=neg => y=0, x=pos => y=1)
    lr = LogisticRegression()
    lr_model = lr.fit(train_spdf)

    return lr_model


@pytest.fixture(scope="module")
def pyspark_svc(pyspark_model):
    svc = PysparkClassifier()
    svc.pack('model', pyspark_model)

    return svc


@pytest.fixture(scope="module")
def pyspark_svc_saved_dir(tmp_path_factory, pyspark_svc):
    """Save a TensorFlow2 BentoService and return the saved directory."""
    tmpdir = str(tmp_path_factory.mktemp("pyspark_svc"))
    pyspark_svc.save_to_dir(tmpdir)

    return tmpdir


@pytest.fixture()
def pyspark_svc_loaded(pyspark_svc_saved_dir):
    """Return a TensorFlow2 BentoService that has been saved and loaded."""
    return bentoml.load(pyspark_svc_saved_dir)


@pytest.fixture()
def pyspark_image(pyspark_svc_saved_dir):
    # Based on `image()` in tests/integration/api_server/conftest.py
    # Better refactoring might be possible to combine both functions
    import docker

    client = docker.from_env()
    image = client.images.build(path=pyspark_svc_saved_dir, tag="example_service", rm=True)[
        0
    ]
    yield image
    client.images.remove(image.id)


@pytest.fixture()
def pyspark_host(pyspark_image):
    # Based on `host()` in tests/integration/api_server/conftest.py
    # Better refactoring might be possible to combine both functions
    import docker

    client = docker.from_env()

    with bentoml.utils.reserve_free_port() as port:
        pass
    command = "bentoml serve-gunicorn /bento --workers 1"
    try:
        container = client.containers.run(
            command=command,
            image=pyspark_image.id,
            auto_remove=True,
            tty=True,
            ports={'5000/tcp': port},
            detach=True,
        )
        _host = f"127.0.0.1:{port}"
        _wait_until_ready(_host, 10)
        yield _host
    finally:
        container.stop()
        time.sleep(1)  # make sure container stopped & deleted


def test_pyspark_artifact(pyspark_svc):
    output_df = pyspark_svc.predict(test_pddf)
    assert list(output_df.prediction) == [0.0, 1.0, 0.0, 1.0]


def test_pyspark_artifact_loaded(pyspark_svc_loaded):
    output_df = pyspark_svc_loaded.predict(test_pddf)
    assert list(output_df.prediction) == [0.0, 1.0, 0.0, 1.0]


@pytest.mark.asyncio
async def test_pyspark_artifact_with_docker(pyspark_host):
    await pytest.assert_request(
        "POST",
        f"http://{pyspark_host}/predict",
        headers=(("Content-Type", "application/json"),),
        data=json.dumps(test_data),
        assert_status=200,
        assert_data=b'[[15.0]]',
    )
