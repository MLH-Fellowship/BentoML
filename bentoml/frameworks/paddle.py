import os

from bentoml.exceptions import MissingDependencyException
from bentoml.service.artifacts import BentoServiceArtifact
from bentoml.service.env import BentoServiceEnv


try:
    import paddle
    from paddle.static import InputSpec
except ImportError:
    paddle = None

class PaddleModelArtifact(BentoServiceArtifact):
    """Abstraction for saving/loading PaddlePaddle models

    Args:
        name (string): name of the artifact

    Raises:
        MissingDependencyException: paddle package is required for PaddleModelArtifact

    Example usage: 
    
    >>> import pandas as pd
    >>>
    >>> from bentoml import env, artifacts, api, BentoService
    >>> from bentoml.adapters import DataframeInput
    >>> from bentoml.frameworks.paddle import PaddleModelArtifact
    >>>
    >>> @env(infer_pip_packages=True)
    >>> @artifacts([PaddleModelArtifact('model')])
    >>> class PaddleService(BentoService):
    >>>    @api(input=DataframeInput(), batch=True)
    >>>    def predict(self, df: pd.DataFrame):
    >>>        input_data = df.to_numpy().astype(np.float32)
    >>>        output_tensor = self.artifacts.model(df)
    >>>        return output_tensor.numpy()
    >>>
    >>> service = PaddleService()
    >>>
    >>> service.pack('model', model_to_save)
    """

    def __init__(self, name:str):
        super(PaddleModelArtifact, self).__init__(name)
        self._model = None

        if paddle is None:
            raise MissingDependencyException(
                "paddlepaddle package is required to use PaddleModelArtifact"
            )
        
    def pack(self, model): # pylint:disable=arguments-differ
        self._model = model
        return self

    def load(self, path):
        model = paddle.jit.load(self._file_path(path))
        model = paddle.jit.to_static(model, input_spec=model._input_spec())
        model.eval()
        return self.pack(model)

    def _file_path(self, base_path):
        return os.path.join(base_path, self.name)
 
    def save(self, dst):
        paddle.jit.save(self._model, self._file_path(dst))

    def get(self):
        return self._model

    def set_dependencies(self, env: BentoServiceEnv):
        env.add_pip_packages(['paddlepaddle'])
