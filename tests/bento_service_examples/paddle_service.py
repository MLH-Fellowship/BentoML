import pandas as pd
import numpy as np

from bentoml import env, artifacts, api, BentoService
from bentoml.adapters import DataframeInput
from bentoml.frameworks.paddle import PaddleModelArtifact

@env(infer_pip_packages=True)
@artifacts([PaddleModelArtifact('model')])
class PaddleService(BentoService):
    @api(input=DataframeInput(), batch=True)
    def predict(self, df: pd.DataFrame):
        input_data = df.to_numpy().astype(np.float32)
        output_tensor = self.artifacts.model(input_data)
        return output_tensor.numpy()