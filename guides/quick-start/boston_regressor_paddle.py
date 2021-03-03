import pandas as pd

from bentoml import env, artifacts, api, BentoService
from bentoml.adapters import DataframeInput
from bentoml.frameworks.paddle import PaddleModelArtifact

@env(infer_pip_packages=True)
@artifacts([PaddleModelArtifact('model')])
class BostonRegressor(BentoService):
    """
    A minimum prediction service exposing a PaddlePaddle model
    """

    @api(input=DataframeInput(), batch=True)
    def predict(self, df: pd.DataFrame):
        """
        An inference API named `predict` with Dataframe input adapter, which codifies
        how HTTP requests or CSV files are converted to a pandas Dataframe object as the
        inference API function input
        """
        return self.artifacts.model(df)