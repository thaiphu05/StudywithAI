import torch
import torch.nn as nn
from transformers import AutoModelForMaskedLM, AutoTokenizer


model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForMaskedLM.from_pretrained(model_id)

class WR_Model(nn.Module):

    def __init__(self, drop_rate=0.2):

        super(WR_Model, self).__init__()
        D_in, D_out = 768, 5
        global model
        global tokenizer
        self.modernbert_masked_lm = model
        self.modernbert_base = self.modernbert_masked_lm.model

        self.regressor = nn.Sequential(
            nn.Dropout(drop_rate),
            nn.Linear(D_in, D_out))

    def forward(self, input_ids, attention_masks):
            outputs = self.modernbert_base(input_ids, attention_mask=attention_masks)
            last_hidden_state = outputs.last_hidden_state
        
            mask = attention_masks.unsqueeze(-1)
            masked = last_hidden_state * mask
        
            sum_embeddings = masked.sum(dim=1)
            sum_mask = mask.sum(dim=1)
        
            mean_pooled = sum_embeddings / sum_mask
        
            outputs = self.regressor(mean_pooled)
            return outputs
    
    def load_model(self, path):
        model = WR_Model(0.2)
        model.load_state_dict(torch.load(path, map_location=torch.device('cpu'), weights_only=True))
        return model, tokenizer
