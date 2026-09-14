import io

import streamlit as st
from PIL import Image

from config import APP_NAME, DEFAULT_SIZE, SUPPORTED_SIZES
from vision_service import analyze_product
from strategy_service import create_listing_plan
from image_service import generate_listing_images
from editor import render_editor
from export_service import prepare_downloads
from database import save_project


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🛒",
    layout="wide",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title("🛒 Atta Visuals")
st.subheader("AI-Powered Amazon Product Listing Visual Generator")

st.caption(
    "Upload one product image → create 7 professional listing visuals "
    "→ edit English/Urdu text → export in high quality."
)


# ---------------------------------------------------------
# SIDEBAR SETTINGS
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    size_options = list(SUPPORTED_SIZES.keys())

    if DEFAULT_SIZE in size_options:
        default_index = size_options.index(DEFAULT_SIZE)
    else:
        default_index = 0

    selected_size = st.selectbox(
        "Output Size",
        options=size_options,
        index=default_index,
    )

    export_format = st.selectbox(
        "Download Format",
        ["PNG", "JPG"],
    )

    st.divider()

    st.info(
        "Groq AI is used for product understanding and listing copy. "
        "The final graphics are rendered locally with Python so the "
        "text remains editable."
    )


# ---------------------------------------------------------
# PRODUCT IMAGE UPLOAD
# ---------------------------------------------------------
uploaded = st.file_uploader(
    "📷 Upload Your Product Image",
    type=["png", "jpg", "jpeg", "webp"],
    help=(
        "Upload one clear product photo. "
        "Avoid collages for better product analysis."
    ),
)


# ---------------------------------------------------------
# OPTIONAL PRODUCT INFORMATION
# ---------------------------------------------------------
product_details = st.text_area(
    "📝 Optional Product Details",
    placeholder=(
        "Add only facts you know, for example:\n"
        "Brand: ABC\n"
        "Material: Stainless Steel\n"
        "Capacity: 1 Liter\n"
        "Dimensions: 20 × 10 cm\n"
        "Compatibility: XYZ"
    ),
)


# ---------------------------------------------------------
# SHOW UPLOADED IMAGE
# ---------------------------------------------------------
if uploaded:

    image_bytes = uploaded.getvalue()

    try:
        product_image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

    except Exception:
        st.error(
            "❌ Unable to read this image. "
            "Please upload a valid PNG, JPG, JPEG, or WEBP image."
        )
        st.stop()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("🖼️ Original Product")

        st.image(
            product_image,
            use_container_width=True,
        )

    with right:
        st.subheader("✨ What Atta Visuals Creates")

        st.markdown(
            """
            **7 Amazon Listing Visuals**

            1. 🖼️ Main Product Image
            2. ⭐ Main Features
            3. 💡 Key Benefits
            4. 📖 How to Use
            5. 📏 Dimensions / Specifications
            6. 🏠 Lifestyle / Real-World Use
            7. 👑 Brand / Premium Closing
            """
        )

        st.divider()

        generate_button = st.button(
            "✨ Generate 7 Listing Images",
            type="primary",
            use_container_width=True,
        )

        # -------------------------------------------------
        # GENERATE LISTING IMAGES
        # -------------------------------------------------
        if generate_button:

            try:

                with st.status(
                    "Creating your listing visuals...",
                    expanded=True,
                ) as status:

                    # STEP 1
                    st.write(
                        "🔍 Step 1/4 — Analyzing product with Groq AI..."
                    )

                    analysis = analyze_product(
                        image_bytes,
                        product_details,
                    )

                    # STEP 2
                    st.write(
                        "🧠 Step 2/4 — Creating 7-image listing strategy..."
                    )

                    plan = create_listing_plan(
                        analysis,
                        product_details,
                    )

                    # STEP 3
                    st.write(
                        "🎨 Step 3/4 — Rendering high-resolution visuals..."
                    )

                    images = generate_listing_images(
                        product_image,
                        plan,
                        selected_size,
                    )

                    # STEP 4
                    st.write(
                        "💾 Step 4/4 — Saving project..."
                    )

                    # Save everything in session
                    st.session_state["analysis"] = analysis
                    st.session_state["plan"] = plan
                    st.session_state["images"] = images
                    st.session_state["original"] = product_image
                    st.session_state["size_name"] = selected_size
                    st.session_state["export_format"] = export_format

                    # Save project to database
                    save_project(
                        analysis,
                        plan,
                    )

                    status.update(
                        label="✅ Done — 7 listing visuals are ready!",
                        state="complete",
                    )

                st.success(
                    "🎉 Your 7 Amazon listing visuals have been created!"
                )

            except Exception as exc:

                st.error(
                    "❌ Generation failed."
                )

                st.exception(exc)


# ---------------------------------------------------------
# EDITOR
# ---------------------------------------------------------
if "images" in st.session_state:

    st.divider()

    st.header("✏️ Edit Your Listing Images")

    st.write(
        "Edit your English or Urdu headline and supporting text "
        "before downloading."
    )

    try:

        edited_images = render_editor(
            st.session_state["images"],
            st.session_state["plan"],
            st.session_state["size_name"],
        )

        st.session_state["images"] = edited_images

    except Exception as exc:

        st.error(
            "❌ Image editor could not be loaded."
        )

        st.exception(exc)


# ---------------------------------------------------------
# DOWNLOAD SECTION
# ---------------------------------------------------------
if "images" in st.session_state:

    st.divider()

    st.header("⬇️ Download Your Images")

    st.write(
        "Download individual images or all 7 visuals together."
    )

    try:

        prepare_downloads(
            st.session_state["images"],
            st.session_state["plan"],
            st.session_state["size_name"],
            st.session_state["export_format"],
        )

    except Exception as exc:

        st.error(
            "❌ Download section could not be loaded."
        )

        st.exception(exc)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "Atta Visuals — Turning One Product Image Into a Complete Amazon Visual Listing."
)
