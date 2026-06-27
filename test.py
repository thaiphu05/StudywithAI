import torch
import torch.nn as nn
from transformers import AutoModelForMaskedLM, AutoTokenizer



model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForMaskedLM.from_pretrained(model_id)

class ModernbertRegressor(nn.Module):

    def __init__(self, drop_rate=0.2):

        super(ModernbertRegressor, self).__init__()
        D_in, D_out = 768, 5
        global model
        self.modernbert_masked_lm = model
        self.modernbert_base = self.modernbert_masked_lm.model

        self.regressor = nn.Sequential(
            nn.Dropout(drop_rate),
            nn.Linear(D_in, D_out))

    def forward(self, input_ids, attention_masks):
        outputs = self.modernbert_base(input_ids, attention_mask=attention_masks)
        class_label_output = outputs.last_hidden_state[:, 0, :]

        outputs = self.regressor(class_label_output)
        return outputs
model_2 = ModernbertRegressor(0.2)

text = """
Many people believe that modern games are not better than traditional games in helping children develop their abilities. To what degree do you support or oppose this idea?Many people believe that modern games are not better than traditional games in helping children develop their abilities. To what degree do you support or oppose this idea?
[SEP] 
In this day and age, it is widely believed that conventional games are superior to modern ones in encouraging children’s ability development. From my perspective, I partly concur with this point of view, mostly because while contemporary ones make an enormous contribution to the young’s growth if they are used properly, traditional games provide a wide range of unique developmental merits.

On the one hand, there is no doubt that traditional, non-digital games, such as hide-and-seek, tag, and board games, play a vital role in developing children’s abilities. Firstly, a huge number of traditional games foster children to engage in outdoor physical activities, helping them improve their fitness levels, and social interaction. In particular, these kinds of games also involve face-to-face communication, which allow children to amplify social skills, including cooperation, conflict-resolution tactics, and emotional control via physical elements and hands-on experiences. Secondly, certain conventional games embrace local culture, as well as moral lessons, which assist children in apprehending societal norms. For instance, activities emphasising fairness and respect for others subtly teach children how to behave in daily life. Hence, not only do traditional game contribute to recreation but they also educate cultural preservation and character development.

On the other hand, it would be misleading to claim that modern games offer no developmental value. First, a number of digital games are designed with an aim to familiarizing children with technology, which is a crucial skill in the digital age. Skills including critical thinking, problem-solving, and decision-making might also be involved and as a result, they can learn how to tackle problems in a variety of contexts. Some educational games incorporate educational opportunities so as to challenge children’s memory, attention, and adaptability. Take puzzle or logic-based games for example, they require children to analyse situations, make decisions, and solve complex challenges. Furthermore, collaboration and teamwork on a global scale are promoted for interaction with diverse cultures and perspectives via online multiplayer games as children often have to communicate and work with others to attain shared goals. Thus, these experiences and exposure both broaden their horizons and foster retention.

In conclusion, whereas traditional games significantly offer both physical and moral benefits, I have to advocate that modern games can notably strengthen both digital and cognitive skills and widen their horizons. Should a balanced approach be utilized, children’s holistic development can be profoundly boosted.
"""

data_test = tokenizer(text=text,add_special_tokens=True,
                            padding='max_length',
                            truncation='longest_first',
                            max_length=1024,
                            return_attention_mask=True)
test_input_ids = data_test['input_ids']
test_masks = data_test['attention_mask']

path = "modernbert_best_model.pth"
model = torch.load(path, map_location=torch.device('cpu'), weights_only=False) 
model_2.load_state_dict(model)
model_2.eval()
print("Model loaded successfully.")

test_input_ids_tensor = torch.tensor(test_input_ids).unsqueeze(0).to("cpu")
test_masks_tensor = torch.tensor(test_masks).unsqueeze(0).to("cpu")
out = model_2(test_input_ids_tensor, test_masks_tensor)
predicted_scaled = out.cpu().detach().numpy().round()
print(predicted_scaled)