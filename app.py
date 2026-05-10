"""
電車に乗りたかザウルス — 東海道新幹線の旅の思い出アプリ（子ども向け）
"""

from __future__ import annotations

import io

import streamlit as st
from PIL import Image

from album_generator import build_album_image
from tokaido_stations import TOKAIDO_STATIONS, route_between

FEELINGS = [
    "😊 たのしかった",
    "😋 おいしかった",
    "😮 びっくりした",
    "😴 ねむかった",
    "🌟 またきたい",
    "🎉 さいこう！",
]

APP_TITLE = "電車に乗りたかザウルス"
DINO = "🦖"


def inject_styles() -> None:
    st.markdown(
        """
<style>
  /* スマホ縦向け想定：中央寄せ・余白（上は絵文字が切れないよう多め） */
  .block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 2rem !important;
    max-width: 520px !important;
    overflow: visible !important;
  }
  /* 恐竜マスコット：絵文字の ascender が欠けないよう行高・パディングを確保 */
  .densha-dino-mascot {
    text-align: center;
    font-size: 3rem;
    line-height: 1.45 !important;
    padding: 0.35rem 0 0.15rem 0;
    margin: 0.25rem 0 0.35rem 0;
    overflow: visible !important;
  }
  /* 大きめボタン */
  div.stButton > button {
    min-height: 3.2rem !important;
    font-size: 1.15rem !important;
    border-radius: 16px !important;
    font-weight: 700 !important;
  }
  /* 見出し */
  h1 { font-size: 1.55rem !important; letter-spacing: 0.02em; }
</style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    defaults = {
        "phase": "home",
        "origin_id": TOKAIDO_STATIONS[0]["id"],
        "dest_id": TOKAIDO_STATIONS[-1]["id"],
        "gotten_off": [],  # list[str]
        "feelings": {},  # station_id -> str
        "photos": {},  # station_id -> bytes
        "goal_celebrated": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_trip() -> None:
    st.session_state.phase = "home"
    st.session_state.gotten_off = []
    st.session_state.feelings = {}
    st.session_state.photos = {}
    st.session_state.goal_celebrated = False


def render_header():
    st.markdown(
        f"<div class='densha-dino-mascot'>{DINO}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"# {APP_TITLE}")
    st.caption("東海道新幹線の旅を 🦖 とおぼえよう！")


def station_labels():
    return [s["name"] for s in TOKAIDO_STATIONS]


def id_by_name(name: str) -> str:
    for s in TOKAIDO_STATIONS:
        if s["name"] == name:
            return s["id"]
    return TOKAIDO_STATIONS[0]["id"]


def name_for_id(sid: str) -> str:
    for s in TOKAIDO_STATIONS:
        if s["id"] == sid:
            return s["name"]
    return TOKAIDO_STATIONS[0]["name"]


def select_index(names: list[str], station_id: str) -> int:
    try:
        return names.index(name_for_id(station_id))
    except ValueError:
        return 0


def feeling_index(sid: str) -> int:
    cur = st.session_state.feelings.get(sid)
    if cur in FEELINGS:
        return FEELINGS.index(cur)
    return 0


def render_home():
    render_header()
    st.markdown("##### どこへいく？")

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚄 あたらしい旅をつくる", use_container_width=True, type="primary"):
            st.session_state.phase = "setup"
            st.rerun()
    with c2:
        if st.button("ℹ️ つかいかた", use_container_width=True):
            st.info(
                "① 出発とゴールをえらぶ → ② えきをタップして「おりた！」→ "
                "③ しゃしんとかんそうをきろく → ④ ゴールでおいわい！ → "
                "⑤ アルバムをほぞんしよう（おとなといっしょにね）"
            )


def render_setup():
    render_header()
    st.markdown("##### ① 出発えき・ゴールえきをえらぶ")

    names = station_labels()
    oc = st.columns(2)
    with oc[0]:
        st.caption("出発（スタート）")
        o_name = st.selectbox(
            "出発",
            names,
            index=select_index(names, st.session_state.origin_id),
            label_visibility="collapsed",
        )
    with oc[1]:
        st.caption("ゴール（もくてきち）")
        d_name = st.selectbox(
            "ゴール",
            names,
            index=select_index(names, st.session_state.dest_id),
            label_visibility="collapsed",
        )

    st.caption("↑ リストからえらんでね（おとなといっしょに）")

    oid = id_by_name(o_name)
    did = id_by_name(d_name)
    st.session_state.origin_id = oid
    st.session_state.dest_id = did

    route = route_between(oid, did)
    r_names = " → ".join(s["name"] for s in route)
    st.success(f"この旅のルート：**{r_names}**")

    b1, b2 = st.columns(2)
    with b1:
        if st.button("🚅 この旅でいく！", use_container_width=True, type="primary"):
            st.session_state.phase = "travel"
            st.session_state.gotten_off = []
            st.session_state.feelings = {}
            st.session_state.photos = {}
            st.session_state.goal_celebrated = False
            st.rerun()
    with b2:
        if st.button("🏠 もどる", use_container_width=True):
            st.session_state.phase = "home"
            st.rerun()


def maybe_celebrate_goal(route: list[dict]):
    dest_id = route[-1]["id"]
    if dest_id in st.session_state.gotten_off and not st.session_state.goal_celebrated:
        st.balloons()
        st.session_state.goal_celebrated = True
        st.toast("🎊 ゴール！おつかれさま！", icon="🦖")


def render_travel():
    render_header()
    route = route_between(st.session_state.origin_id, st.session_state.dest_id)
    dest_id = route[-1]["id"]

    st.markdown("##### ② 路線図（タップしておりたえきをきろく）")
    st.caption("おりたえきだけ 🦖 がつくよ。ゴールえきでおいわい！")

    # 縦の路線：カードを積み上げ（起点を上に）
    for i, stinfo in enumerate(route):
        sid = stinfo["id"]
        is_dest = sid == dest_id
        got = sid in st.session_state.gotten_off

        # カード開始（見た目用にマーカーを先に）
        line_html = ""
        if i < len(route) - 1:
            line_html = (
                "<div style='text-align:center;margin:-6px 0 4px 0;font-size:1.6rem;'>"
                "┊<br/>▼</div>"
            )

        label = "🏁 ゴール！" if is_dest and sid == route[-1]["id"] else ""
        if i == 0:
            label = "🚉 スタート（出発）"

        with st.container(border=True):
            if label:
                st.markdown(f"<div style='text-align:center;color:#b45309;font-weight:700;'>{label}</div>", unsafe_allow_html=True)

            title_row = f"### {stinfo['name']}"
            st.markdown(title_row)

            if not got:
                if st.button(
                    "おりた！（タップ）",
                    key=f"off_{sid}",
                    use_container_width=True,
                    type="primary",
                ):
                    if sid not in st.session_state.gotten_off:
                        st.session_state.gotten_off.append(sid)
                        st.session_state.feelings.setdefault(sid, FEELINGS[0])
                    st.rerun()
            else:
                row = st.columns([1, 2])
                with row[0]:
                    st.markdown(
                        f"<div class='densha-dino-mascot' style='margin:0'>{DINO}</div>",
                        unsafe_allow_html=True,
                    )
                    thumb = st.session_state.photos.get(sid)
                    if thumb:
                        st.image(Image.open(io.BytesIO(thumb)), use_container_width=True)
                    else:
                        st.markdown(
                            "<div style='text-align:center;padding:12px;background:#f8fafc;border-radius:12px;'>"
                            "📷 まだない</div>",
                            unsafe_allow_html=True,
                        )
                with row[1]:
                    st.markdown("**おりたよ！**")
                    feel = st.radio(
                        "きょうのきもち（ひとつ）",
                        FEELINGS,
                        key=f"feel_{sid}",
                        horizontal=False,
                        label_visibility="collapsed",
                        index=feeling_index(sid),
                    )
                    st.session_state.feelings[sid] = feel

                    up = st.file_uploader(
                        "しゃしんをいれる（1まい）",
                        type=["jpg", "jpeg", "png", "webp"],
                        key=f"up_{sid}",
                        label_visibility="collapsed",
                    )
                    if up is not None:
                        data = up.getvalue()
                        if st.session_state.photos.get(sid) != data:
                            st.session_state.photos[sid] = data
                            st.rerun()

        st.markdown(line_html, unsafe_allow_html=True)

    maybe_celebrate_goal(route)

    st.divider()
    ec1, ec2 = st.columns(2)
    with ec1:
        if st.button("📒 旅を終える（アルバムへ）", use_container_width=True, type="primary"):
            st.session_state.phase = "album"
            st.rerun()
    with ec2:
        if st.button("🏠 ホームへ", use_container_width=True):
            reset_trip()
            st.rerun()


def render_album():
    render_header()
    st.markdown("##### ③ 旅のアルバムをつくる")

    route = route_between(st.session_state.origin_id, st.session_state.dest_id)
    gotten = [s for s in st.session_state.gotten_off if s in {x["id"] for x in route}]

    if not gotten:
        st.warning("まだ「おりた！」がないよ。もどってえきをタップしてね。")
        if st.button("もどる（旅へ）", type="primary"):
            st.session_state.phase = "travel"
            st.rerun()
        return

    png = build_album_image(
        route,
        gotten,
        st.session_state.photos,
        st.session_state.feelings,
    )
    st.success("できあがり！おとなとしゃしんをほぞんしよう 📷")

    st.download_button(
        label="📥 アルバム画像をほぞん（PNG）",
        data=png,
        file_name="denshaninoritaka_album.png",
        mime="image/png",
        use_container_width=True,
        type="primary",
    )

    st.image(png, caption="プレビュー", use_container_width=True)

    if st.button("🔄 もういちどあたらしい旅", use_container_width=True):
        reset_trip()
        st.rerun()


def main():
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🦖",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    init_state()
    inject_styles()

    phase = st.session_state.phase
    if phase == "home":
        render_home()
    elif phase == "setup":
        render_setup()
    elif phase == "travel":
        render_travel()
    elif phase == "album":
        render_album()
    else:
        st.session_state.phase = "home"
        render_home()


if __name__ == "__main__":
    main()
