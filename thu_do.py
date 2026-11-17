
# thu_do.py — Thử đồ ảo qua Hugging Face Spaces
# Áo: IDM-VTON (dự phòng Change-Clothes-AI)
# Quần/chân váy, váy liền: Change-Clothes-AI (dự phòng OOTDiffusion)

import os
import tempfile
import inspect
import hashlib
import shutil
from pathlib import Path

from gradio_client import Client, handle_file


SPACE = {
    "idm": "yisol/IDM-VTON",
    "cc": "jallenjia/Change-Clothes-AI",
    "ootd": "levihsu/OOTDiffusion"
}

LOAI_CC = {
    "upper": "upper_body",
    "lower": "lower_body",
    "dress": "dresses"
}

LOAI_OOTD = {
    "upper": "Upper-body",
    "lower": "Lower-body",
    "dress": "Dress"
}

THU_TU = {
    "upper": ["idm", "cc"],
    "lower": ["cc", "ootd"],
    "dress": ["cc", "ootd"]
}

KHO_ANH = Path(__file__).parent / "ket_qua" / "thu_do"
_client = {}


# ================= KẾT NỐI MÔ HÌNH

def _lay_hf_token():
    """Lấy Hugging Face token từ biến môi trường hoặc Streamlit Secrets."""
    tk = (
        os.environ.get("HF_TOKEN")
        or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    )

    if tk:
        return tk.strip()

    # Hỗ trợ triển khai trên Streamlit Cloud:
    # Settings > Secrets, khai báo HF_TOKEN = "hf_..."
    try:
        import streamlit as st
        tk = st.secrets.get("HF_TOKEN")
        if not tk:
            hf_cfg = st.secrets.get("huggingface", {})
            if hasattr(hf_cfg, "get"):
                tk = hf_cfg.get("HF_TOKEN") or hf_cfg.get("token")
    except Exception:
        tk = None

    return str(tk).strip() if tk else None


def _ket_noi(ten):
    if ten not in _client:
        tk = _lay_hf_token()
        ts = inspect.signature(Client.__init__).parameters

        # Tên tham số xác thực thay đổi tùy phiên bản gradio_client.
        kw = {}
        if tk:
            if "hf_token" in ts:
                kw["hf_token"] = tk
            elif "token" in ts:
                kw["token"] = tk
            else:
                raise RuntimeError(
                    "Phiên bản gradio_client hiện tại không hỗ trợ truyền "
                    "Hugging Face token. Hãy cập nhật gradio_client."
                )

        _client[ten] = Client(SPACE[ten], **kw)

    return _client[ten]


# ================= ẢNH TẠM

def _luu_tam(im):
