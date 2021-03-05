import paddle
import numpy as np
import pandas as pd
import bentoml
from paddle.static import InputSpec
from paddle_service import PaddleService

BATCH_SIZE = 8
BATCH_NUM = 4
EPOCH_NUM = 5

IN_FEATURES = 13
OUT_FEATURES = 1

class LinearNet(paddle.nn.Layer):
    def __init__(self):
        super(LinearNet, self).__init__()
        self._linear = paddle.nn.Linear(IN_FEATURES, OUT_FEATURES)

    @paddle.jit.to_static(input_spec=[InputSpec(shape=[IN_FEATURES], dtype='float32')])
    def forward(self, x):
        return self._linear(x)

def train(model, loader, loss_fn, opt):
    for epoch_id in range(EPOCH_NUM):
        for batch_id, (image, label) in enumerate(loader()):
            out = model(image)
            loss = loss_fn(out, label)
            loss.backward()
            opt.step()
            opt.clear_grad()
            print("Epoch {} batch {}: loss = {}".format(
                epoch_id, batch_id, np.mean(loss.numpy())))

if __name__ == "__main__":
    model = LinearNet()
    loss_fn = paddle.nn.MSELoss()
    adam = paddle.optimizer.Adam(parameters=model.parameters())

    dataset = paddle.text.datasets.UCIHousing(mode="train")

    loader = paddle.io.DataLoader(dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    drop_last=True,
    num_workers=2)

    train(model, loader, loss_fn, adam)

    bento_service = PaddleService()
    bento_service.pack('model', model)

    # Save the model
    saved_path = bento_service.save()

    # Load the model
    loaded_model = bentoml.load(saved_path)

    test_x = pd.DataFrame([[-0.0405441 ,  0.06636364, -0.32356227, -0.06916996, -0.03435197,
        0.05563625, -0.03475696,  0.02682186, -0.37171335, -0.21419304,
       -0.33569506,  0.10143217, -0.21172912]])

    pred = loaded_model.predict(test_x)
    print(pred)