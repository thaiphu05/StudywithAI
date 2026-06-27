import torch
import torch.nn as nn
from transformers import AutoModelForMaskedLM, AutoTokenizer

model_id = "answerdotai/ModernBERT-base"


class WR_Model(nn.Module):

    def __init__(
        self,
        backbone,
        hidden_dim=256,
        num_labels=5,
        drop_rate=0.2,
    ):
        super().__init__()

        self.backbone = backbone
        self.config = backbone.config
        hidden_size = self.backbone.config.hidden_size

        self.regressor = nn.Sequential(
            nn.Linear(hidden_size, hidden_dim),
            nn.GELU(),
            nn.Dropout(drop_rate),
            nn.Linear(hidden_dim, num_labels)
        )

    def mean_pooling(self, hidden_states, attention_mask):
        mask = attention_mask.unsqueeze(-1).float()
        summed = (hidden_states * mask).sum(dim=1)
        counts = mask.sum(dim=1).clamp(min=1e-9)
        return summed / counts

    def forward(self, input_ids, attention_mask, **kwargs):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        pooled = self.mean_pooling(outputs.last_hidden_state, attention_mask)
        logits = self.regressor(pooled)
        return logits

    @staticmethod
    def load_model(path):
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        backbone = AutoModelForMaskedLM.from_pretrained(model_id).model
        model = WR_Model(backbone=backbone)
        state = torch.load(path, map_location=torch.device("cpu"), weights_only=True)
        model.load_state_dict(state)
        return model, tokenizer
