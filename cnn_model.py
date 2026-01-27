import torch.nn as nn


class EncoderDecoder(nn.Module):
    def __init__(self):
        super(EncoderDecoder, self).__init__()

        self.encoder = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(32),

            nn.AvgPool2d(kernel_size=3, stride=2, padding=1),

            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(64),

            nn.AvgPool2d(kernel_size=3, stride=2, padding=1),

            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            nn.BatchNorm2d(128),

            nn.AvgPool2d(kernel_size=3, stride=2, padding=1),
        )

        self.bottleneck = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=1, stride=1, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout2d(0.3),
        )

        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),

            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),

            nn.ConvTranspose2d(32, 4, kernel_size=3, stride=2, padding=1, output_padding=1),
            # nn.Sigmoid(),
        )

    def forward(self, x):
        encoded = self.encoder(x)
        bottleneck = self.bottleneck(encoded)
        decoded = self.decoder(bottleneck)
        return decoded


class EncoderDecoderWithConnections(nn.Module):
    def __init__(self):
        super(EncoderDecoderWithConnections, self).__init__()

        self.pool = nn.AvgPool2d(kernel_size=3, stride=2, padding=1)

        self.encoder1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
        )

        self.encoder2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
        )

        self.encoder3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
        )

        self.bottleneck = nn.Sequential(
            nn.Conv2d(128, 128, kernel_size=1, stride=1, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout2d(0.3),
        )

        self.decoder1 = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1),
            # nn.BatchNorm2d(64),
            nn.ReLU(),
        )

        self.decoder2 = nn.Sequential(
            nn.ConvTranspose2d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),
            # nn.BatchNorm2d(32),
            nn.ReLU(),
        )

        self.decoder3 = nn.Sequential(
            nn.ConvTranspose2d(32, 4, kernel_size=3, stride=2, padding=1, output_padding=1),
            # nn.Sigmoid(),
        )

        self.batchNorm128 = nn.BatchNorm2d(128)
        self.batchNorm64 = nn.BatchNorm2d(64)
        self.batchNorm32 = nn.BatchNorm2d(32)

    def forward(self, x):

        encoded_1 = self.pool(self.encoder1(x))
        encoded_2 = self.pool(self.encoder2(encoded_1))
        encoded_3 = self.pool(self.encoder3(encoded_2))

        bottleneck = self.bottleneck(encoded_3)

        decoded_1 = self.decoder1(self.batchNorm128(encoded_3 + bottleneck))
        decoded_2 = self.decoder2(self.batchNorm64(decoded_1 + encoded_2))
        decoded_3 = self.decoder3(self.batchNorm32(decoded_2 + encoded_1))

        return decoded_3
