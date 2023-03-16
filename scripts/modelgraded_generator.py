# generate a jsonl where each line is a sample

import json
import os
import string
from typing import Any

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "../evals/registry")


def format(template: str, **kwargs: dict[str, str]) -> str:
    """Format a template string with kwargs."""
    keys = [k[1] for k in string.Formatter().parse(template) if k[1]]
    assert all(k in kwargs for k in keys), f"Required: {keys}, got: {sorted(kwargs)}"
    cur_keys = {k: kwargs[k] for k in keys}
    return template.format(**cur_keys)


YAML = """
mg-{prompt_name}-{subject}:
  id: mg-{prompt_name}-{subject}.dev.v0
  metrics: [accuracy]
mg-{prompt_name}-{subject}.dev.v0:
  class: evals.elsuite.modelgraded.classify:ModelBasedClassify
  args:
    samples_jsonl: test_modelgraded/{prompt_name}_{subject}.jsonl
    eval_type: {eval_type}
    modelgraded_spec_file: {modelgraded_spec_file}
""".strip()


unlabeled_prompts = dict(
    humor=dict(
        modelgraded_spec_file="humor_jp",
        prompt="{subject}での大喜利を書いて。敬語じゃなく関西弁で吉本のM1チャンピョンみたいに書いて。",
        eval_type="cot_classify_jp",
    ),
)


subjects = dict(
    animals=["cat", "bird", "hamster"],
    fruits=["apple", "banana", "orange"],
    people=["Elon Musk", "Bill Gates", "Jeff Bezos"],
    people_jp=["イーロン・マスク", "ビル・ゲイツ", "ジェフ・ベゾス"],
)

unlabeled_target_sets = [
    ("humor", "people_jp"),
]

data_dir = f"{REGISTRY_PATH}/data/test_modelgraded"
yaml_str = f"# This file is generated by {os.path.basename(__file__)}\n\n"
for prompt_name, subject in unlabeled_target_sets:
    prompt = unlabeled_prompts[prompt_name]["prompt"]
    samples = [{"input": format(prompt, subject=s)} for s in subjects[subject]]
    file_name = f"{data_dir}/{prompt_name}_{subject}.jsonl"
    # save samples jsonl
    with open(file_name, "wb") as f:
        for sample in samples:
            # f.write(json.dumps(sample) + "\n")
            json_data = json.dumps(sample, ensure_ascii=False)
            f.write(json_data.encode("utf-8"))
            f.write(b"\n")
    print(f"wrote {len(samples)} samples to {file_name}")
    yaml_str += (
        YAML.format(
            prompt_name=prompt_name,
            subject=subject,
            modelgraded_spec_file=unlabeled_prompts[prompt_name]["modelgraded_spec_file"],
            eval_type=unlabeled_prompts[prompt_name]["eval_type"],
        )
        + "\n\n"
    )


yaml_file = f"{REGISTRY_PATH}/evals/test-modelgraded-generated.yaml"
with open(yaml_file, "w") as f:
    f.write(yaml_str)
print(f"wrote {yaml_file}")