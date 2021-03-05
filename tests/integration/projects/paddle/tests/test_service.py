import pandas

test_df = pandas.DataFrame([[-0.0405441 ,  0.06636364, -0.32356227, -0.06916996, -0.03435197,
        0.05563625, -0.03475696,  0.02682186, -0.37171335, -0.21419304,
       -0.33569506,  0.10143217, -0.21172912]])

def test_paddle_artifact_pack(service):
    assert service.predict(test_df) == [[0.68886477]], 'Run inference before saving'
    
    saved_path = service.save()
    loaded_service = bentoml.load(saved_path)
    assert loaded_service.predict(test_df) == [[0.68886477]], 'Run inference from saved model'