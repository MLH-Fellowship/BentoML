import pathlib
import sys

import numpy as np

import bentoml
from bentoml.adapters import DataframeInput
from bentoml.frameworks.paddle import PaddleModelArtifact


@bentoml.env(infer_pip_packages=True)
@bentoml.artifacts([PaddleModelArtifact('model')])
class PaddleService(bentoml.BentoService):
    @bentoml.api(input=DataframeInput(), batch=True)
    def predict(self, df):
        input_data = df.to_numpy().astype(np.float32)
        output_tensor = self.artifacts.model(input_data)
        return output_tensor.numpy()


if __name__ == "__main__":
    artifacts_path = sys.argv[1]
    bento_dist_path = sys.argv[2]
    service = PaddleService()

    from model.model import Model  # noqa # pylint: disable=unused-import

    service.artifacts.load_all(artifacts_path)

    print("INPUT SPEC FROM SERVICE: ", service.artifacts.model)
    print("PROGRAM FROM SERVICE: ", service.artifacts.model.program())
    pathlib.Path(bento_dist_path).mkdir(parents=True, exist_ok=True)
    service.save_to_dir(bento_dist_path)
