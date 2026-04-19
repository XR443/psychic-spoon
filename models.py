import torch
import torch.nn as nn

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class ImageCaptionModel(nn.Module):
    def __init__(self, vocab_size, pad_idx):
        super(ImageCaptionModel, self).__init__()

        self.n_hidden = 512
        self.embedding_dim = self.n_hidden
        self.n_layers = 3
        self.dropout = 0.3

        self.encoder = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1),
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

            nn.Flatten(),
            nn.Linear(128 * 64 * 64, self.n_hidden),
            nn.Tanh(),
            nn.Dropout(self.dropout),
        )

        self.embedding = nn.Sequential(
            nn.Embedding(vocab_size, self.embedding_dim, padding_idx=pad_idx),
            nn.Dropout(self.dropout),
        )

        self.lstm = nn.LSTM(input_size=self.n_hidden,
                            hidden_size=self.n_hidden, num_layers=self.n_layers,
                            dropout=self.dropout, batch_first=True)

        self.fc = nn.Sequential(
            nn.Linear(self.n_hidden, vocab_size),
        )

    def forward(self, x, prev, hidden=None):
        if hidden is None:
            encoded = self.encoder(x)
            squeezed = encoded.unsqueeze(0).repeat(self.n_layers, 1, 1)
            hidden = (torch.zeros(squeezed.shape).to(device), squeezed)

        embedded = self.embedding(prev)

        r_output, (hidden, cell) = self.lstm(embedded, hidden)

        result = self.fc(r_output)

        return result, (hidden, cell)


class LanguageModelling(nn.Module):
    def __init__(self, vocab_size, pad_idx):
        super(LanguageModelling, self).__init__()

        self.hidden_dim = 1024
        self.embedding_dim = 512
        self.num_layers = 3
        self.dropout = .3

        self.embedding = nn.Sequential(
            nn.Embedding(vocab_size, self.embedding_dim, padding_idx=pad_idx),
            nn.Dropout(self.dropout),
        )

        self.lstm = nn.LSTM(self.embedding_dim, self.hidden_dim, self.num_layers,
                            batch_first=True, dropout=self.dropout if self.num_layers > 1 else 0)

        self.fc_out = nn.Sequential(
            nn.Linear(self.hidden_dim, vocab_size),
            nn.Dropout(self.dropout),
        )

    def forward(self, x, hidden_state=None):
        """
        x: (batch, seq_len)
        returns: outputs (batch, vocab_size),
                 hidden (num_layers, batch, hidden_dim),
                 cell (num_layers, batch, hidden_dim)
        """
        embedded = self.embedding(x)

        if hidden_state is None:
            output, (hidden, cell) = self.lstm(embedded)
        else:
            output, (hidden, cell) = self.lstm(embedded, hidden_state)

        return self.fc_out(output), (hidden, cell)
