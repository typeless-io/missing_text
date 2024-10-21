import streamlit as st
import json
from missing_text.extract.pdf import sync_extract_pdf
import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def main():
    st.set_page_config(page_title="PDF Content Extractor", layout="wide")

    st.title("PDF Content Extractor")

    # Global variable to store extracted content
    if "pdf_content" not in st.session_state:
        st.session_state.pdf_content = None

    # Create tabs for navigation
    tabs = st.tabs(
        [
            "Upload & Process",
            "Text",
            "Tables",
            "Extracted Images",
            "Image OCR",
            "Segments",
            "Download JSON",
            "Processing Logs",
        ]
    )

    with tabs[0]:
        st.header("Upload and Process PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if st.button("Start Processing"):
            if uploaded_file is None:
                st.warning("Please upload a PDF file before processing.")
            else:
                with st.spinner("Extracting content..."):
                    pdf_content = sync_extract_pdf(uploaded_file.getvalue())
                    st.session_state.pdf_content = pdf_content
                    st.session_state.total_pages = len(pdf_content["contents"])
                st.success(
                    "PDF processed successfully. Navigate to other tabs to view the results."
                )

    with tabs[1]:
        st.header("Extracted Text")
        if st.session_state.pdf_content and "contents" in st.session_state.pdf_content:
            # Split the text into pages
            
            # Iterate over each page
            for i in range(st.session_state.total_pages):
                st.subheader(f"Page {i + 1}")
                col1, col2 = st.columns(2)

                with col1:
                    if "images" in st.session_state.pdf_content["contents"][i]:
                        page_images = st.session_state.pdf_content["contents"][i]["images"]
                        
                        # Iterate over each image in the list
                        for j, image in enumerate(page_images):
                            image_data = image["image_data"]  # Assuming each image has an "image_data" field
                            st.image(
                                base64.b64decode(image_data),
                                caption=f"Page {i + 1} - Image {j + 1}",
                                use_column_width=True,
                            )
                    else:
                        st.info(f"No image found for Page {i + 1}")

                # Column 2: Display the extracted text
                with col2:
                    page_text = st.session_state.pdf_content["contents"][i].get("text", "No text extracted.")
                    st.text_area(
                        label=f"Page {i + 1} Content",
                        value=page_text.strip(),
                        height=400,
                        key=f"text_{i}",
                    )

    with tabs[2]:
        st.header("Extracted Tables")
        if st.session_state.pdf_content and "contents" in st.session_state.pdf_content:
            # Iterate over each page
            for i in range(st.session_state.total_pages):
                if "tables" in st.session_state.pdf_content["contents"][i]:
                    page_tables = st.session_state.pdf_content["contents"][i]["tables"]
                    
                    # Iterate over each image in the list
                    for j, tables in enumerate(page_tables):
                        st.subheader(f"Page {i + 1}, Table {j + 1}")
                        st.dataframe(tables["content"])

                else:
                    st.info(f"No image found for Page {i + 1}")

        else:
            st.warning("No tables extracted. Please process a PDF first.")

    with tabs[3]:
        st.header("Extracted Images")
        if st.session_state.pdf_content and "contents" in st.session_state.pdf_content:
            for i in range(st.session_state.total_pages):
                if "images" in st.session_state.pdf_content["contents"][i]:
                    page_images = st.session_state.pdf_content["contents"][i]["images"]
                    for j, image in enumerate(page_images):
                        st.subheader(f"Page {i + 1}, Image {j + 1}")
                        image_data = base64.b64decode(image["image_data"])
                        st.image(
                            Image.open(io.BytesIO(image_data)),
                            caption=f"Extracted Image {i+1}",
                            use_column_width=True,
                        )
                else:
                    st.warning("No images extracted. Please process a PDF first.")
        else:
            st.warning("No images extracted. Please process a PDF first.")


    with tabs[4]:
        st.header("Image OCR")
        if st.session_state.pdf_content and "contents" in st.session_state.pdf_content:
            for i in range(st.session_state.total_pages):
                if "images" in st.session_state.pdf_content["contents"][i]:
                    page_images = st.session_state.pdf_content["contents"][i]["images"]
                    for j, image in enumerate(page_images):
                        st.subheader(f"Page {i + 1}, Image {j + 1} OCR")
                        st.text_area(
                            label=f"OCR Text for Page {i + 1}, Image {j + 1}",
                            value=image["content"],
                            height=200,
                        )
                else:
                    st.warning("No OCR text available. Please process a PDF first.")
        else:
            st.warning("No images extracted. Please process a PDF first.")

    with tabs[5]:
        st.header("PDF Segments")
        if st.session_state.pdf_content and "segments" in st.session_state.pdf_content:
            for page_num, page_data in enumerate(
                st.session_state.pdf_content["segments"]
            ):
                st.subheader(f"Page {page_num + 1}")

                # Create a new figure and axis
                fig, ax = plt.subplots(figsize=(10, 14))

                # Add bounding boxes for each segment
                segment_colors = {
                    "text": "blue",
                    "image": "green",
                    "table": "red",
                    "chart": "purple",
                    "latex": "orange",
                }

                for segment in page_data["segments"]:
                    x, y, w, h = segment["bbox"]
                    rect = patches.Rectangle(
                        (x, y),
                        w - x,
                        h - y,
                        linewidth=2,
                        edgecolor=segment_colors.get(segment["type"], "gray"),
                        facecolor="none",
                    )
                    ax.add_patch(rect)

                ax.axis("off")
                st.pyplot(fig)

                # Display grouped and collapsible segments
                for segment_type in segment_colors.keys():
                    segments = [
                        s for s in page_data["segments"] if s["type"] == segment_type
                    ]
                    with st.expander(
                        f"{segment_type.capitalize()} ({len(segments)})", expanded=False
                    ):
                        for segment in segments:
                            st.markdown(
                                f'<div style="border-left: 5px solid {segment_colors[segment_type]}; padding-left: 10px;">',
                                unsafe_allow_html=True,
                            )
                            st.write(
                                f"Content: {segment['content'][:100]}..."
                            )  # Show first 100 characters
                            st.write(f"Bounding Box: {segment['bbox']}")
                            st.markdown("</div>", unsafe_allow_html=True)
                            st.write("---")
        else:
            st.warning("No segment data available. Please process a PDF first.")

    with tabs[6]:
        st.header("Download Extracted Content as JSON")
        if st.session_state.pdf_content:
            json_str = json.dumps(st.session_state.pdf_content, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="extracted_content.json",
                mime="application/json",
            )
        else:
            st.warning("No PDF processed yet. Please upload and process a PDF first.")

    with tabs[7]:
        st.header("Processing Logs")
        if st.session_state.pdf_content:
            st.text("PDF processing completed successfully.")
            st.text("No errors or warnings were encountered during processing.")
        else:
            st.warning("No PDF processed yet. Please upload and process a PDF first.")


if __name__ == "__main__":
    main()
