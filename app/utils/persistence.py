import fsspec
import pydantic
import typing
import yaml
import hashlib
import streamlit as st
import json
import contextlib
import os
import functools
import shutil
import tempfile

if "config" not in st.session_state:
    with open('config.yaml', 'r', encoding='utf-8') as file:
        st.session_state.config = yaml.load(file, Loader=yaml.SafeLoader)

persistence_base = st.session_state.config.get(
    "persistence", {}).get("base", "file:.")

class PersistedModel(pydantic.BaseModel):
    persisted_at: typing.Optional[str] = None

    def __init__(self, **data: typing.Any):
        if "__jsonclass__" in data:
            persisted_at = data.pop("__jsonclass__")[1]
            with fsspec.open(persisted_at, "r") as f:
                data = json.load(f)
                data["persisted_at"] = persisted_at
        super().__init__(**data)

    @pydantic.model_serializer(mode='wrap')
    def ser_model(self, handler: pydantic.SerializerFunctionWrapHandler, info: pydantic.SerializationInfo) -> dict[str, typing.Any]:
        value = handler(self)
        value.pop("persisted_at")
        value_json = json.dumps(value, sort_keys=True).encode("utf-8")
        model_id = hashlib.sha256(value_json).hexdigest()

        if not self.persisted_at or self.persisted_at.split("/")[-1].split(".json")[0] != model_id:
            self.persisted_at = "%s/%s.json" % (persistence_base, model_id)
            with fsspec.open(self.persisted_at, "wb") as f:
                f.write(value_json)
        return {"__jsonclass__": ["persisted_at", self.persisted_at]}

    def persist(self):
        return self.model_dump()["__jsonclass__"][1]

@contextlib.contextmanager
def write_persisted_file(suffix="", mode="wb"):
    """
    Usage:

    with write_persisted_file(".png", "wb") as f:
        f.write(pngimagedata)
    # After the with-block, persisted_at = f.url
    """
    assert "w" in mode
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        with open(temp.name, mode) as ftemp:
            yield ftemp  # Just yield ftemp, no need to assign ftemp.name
        with open(temp.name, "rb") as f:
            hsh = hashlib.sha256()
            for block in iter(functools.partial(f.read, 1024), b''):
                hsh.update(block)  # <-- Also fix typo: you used 'chunk' instead of 'block'!
        content_id = hsh.hexdigest()
        ftemp_url = "%s/%s%s" % (persistence_base, content_id, suffix)
        with fsspec.open(ftemp_url, "wb") as fout:
            with open(temp.name, "rb") as fin:
                shutil.copyfileobj(fin, fout)
        ftemp.url = ftemp_url  # <-- Assign URL here AFTER processing
    finally:
        os.remove(temp.name)

def persist_file(local_file, name):
    with write_persisted_file(suffix = "." + name.rsplit(".", 1)[1]) as outf:
        shutil.copy(local_file, outf)
    return outf.url

    
if __name__ == "__main__":
    class LongStory(PersistedModel):
        instruction: str
        plan_steps: list[str]
        story: str

    dmp = LongStory(instruction="foo", plan_steps=["bar", "fie"], story="gazonk").model_dump()
    print(dmp)
    # {'__jsonclass__': ['persisted_at', 'file:./25677a0a2b873ce58ea463b17c1c4b2add790b687e9284be0ce7627a122d7d38.json']}
    print(LongStory(**dmp))
    # persisted_at='file:./25677a0a2b873ce58ea463b17c1c4b2add790b687e9284be0ce7627a122d7d38.json' instruction='foo' plan_steps=['bar', 'fie'] story='gazonk'
    print(LongStory(**dmp).model_dump())
    # {'__jsonclass__': ['persisted_at', 'file:./25677a0a2b873ce58ea463b17c1c4b2add790b687e9284be0ce7627a122d7d38.json']}
    s = LongStory(instruction="foo", plan_steps=["bar", "fie"], story="gazonk")
    print(s.model_dump())
    # {'__jsonclass__': ['persisted_at', 'file:./25677a0a2b873ce58ea463b17c1c4b2add790b687e9284be0ce7627a122d7d38.json']}
    s.instruction = "bar"
    print(s.model_dump())
    # {'__jsonclass__': ['persisted_at', 'file:./29e314a34d16f29731381b852e7d33b6277b7d40400c28fcd4941de9d202bacd.json']}
