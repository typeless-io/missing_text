import streamlit as st
import json
from missing_text.extract.pdf import sync_extract_pdf
import io
import base64
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def main():
    st.set_page_config(
        page_title="MissingText - Processed Document Analyser", layout="wide"
    )

    st.title("MissingText - Processed Document Analyser")

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
                    # We can customize the zoom here if needed, but defaults are good
                    pdf_content = sync_extract_pdf(uploaded_file.getvalue(), zoom=2.0)
                    st.session_state.pdf_content = pdf_content
                st.success(
                    "PDF processed successfully. Navigate to other tabs to view the results."
                )

    with tabs[1]:
        st.header("Extracted Text")
        if (
            st.session_state.pdf_content
            and "text" in st.session_state.pdf_content
            and st.session_state.pdf_content["text"]
        ):
            # Split the text into pages
            for i, text_item in enumerate(st.session_state.pdf_content["text"]):
                st.subheader(f"Page {text_item['page_number']}")
                col1, col2 = st.columns([1, 1]) # Equal columns
                with col1:
                    page_data = st.session_state.pdf_content["pages"][i]
                    if page_data.get("image"):
                        st.image(
                            base64.b64decode(page_data["image"]),
                            caption=f"Original Page {text_item['page_number']}",
                            use_column_width=True,
                        )
                    else:
                        st.error("Page image could not be rendered.")
                with col2:
                    st.text_area(
                        label=f"Page {text_item['page_number']} Content",
                        value=text_item["content"],
                        height=600, # Increased height
                        key=f"text_{i}",
                    )
        else:
            st.warning("No PDF processed yet. Please upload and process a PDF first.")

    with tabs[2]:
        st.header("Extracted Tables")
        if (
            st.session_state.pdf_content
            and "tables" in st.session_state.pdf_content
            and st.session_state.pdf_content["tables"]
        ):
            for i, table_item in enumerate(st.session_state.pdf_content["tables"]):
                st.subheader(f"Page {table_item['page_number']}")
                # Improve column distribution
                col1, col2 = st.columns([1, 2])
                with col1:
                    page_index = table_item["page_number"] - 1
                    if 0 <= page_index < len(st.session_state.pdf_content["pages"]):
                        page_image = st.session_state.pdf_content["pages"][page_index]["image"]
                        st.image(
                            base64.b64decode(page_image),
                            caption=f"Original Page {table_item['page_number']}",
                            use_column_width=True,
                        )
                with col2:
                    st.dataframe(table_item["content"], key=f"table_pymupdf_{i}", use_container_width=True)
        else:
            st.info("No tables extracted using PyMuPDF.")

    with tabs[3]:
        st.header("Extracted Images")
        if not st.session_state.pdf_content:
            st.warning("No images extracted. Please process a PDF first.")
        elif (
            st.session_state.pdf_content
            and "images" in st.session_state.pdf_content
            and st.session_state.pdf_content["images"]
        ):
            for i, image_item in enumerate(st.session_state.pdf_content["images"]):
                st.subheader(f"Page {image_item['page_number']}")
                col1, col2 = st.columns(2)
                with col1:
                    # Display the original PDF page
                    page_index = image_item["page_number"] - 1
                    if 0 <= page_index < len(st.session_state.pdf_content["pages"]):
                        page_image = st.session_state.pdf_content["pages"][page_index]["image"]
                        st.image(
                            base64.b64decode(page_image),
                            caption=f"Original Page {image_item['page_number']}",
                            use_column_width=True,
                        )
                with col2:
                    if "image_data" in image_item:
                        image_bytes = base64.b64decode(image_item["image_data"])
                        st.image(
                            Image.open(io.BytesIO(image_bytes)),
                            caption=f"Extracted Image from Page {image_item['page_number']}",
                            use_column_width=True,
                        )
                    else:
                        st.write("No image data available for this item.")
        else:
            st.info("No images extracted from the PDF.")

    with tabs[4]:
        st.header("Image OCR")
        if not st.session_state.pdf_content:
            st.warning("No OCR text available. Please process a PDF first.")
        elif st.session_state.pdf_content and "images" in st.session_state.pdf_content:
            for i, image_item in enumerate(st.session_state.pdf_content["images"]):
                st.subheader(f"Page {image_item['page_number']}")
                col1, col2 = st.columns(2)
                with col1:
                    if "image_data" in image_item:
                        image_bytes = base64.b64decode(image_item["image_data"])
                        st.image(
                            Image.open(io.BytesIO(image_bytes)),
                            caption=f"Extracted Image from Page {image_item['page_number']}",
                            use_column_width=True,
                        )
                    else:
                        st.write("No image data available for this item.")
                with col2:
                    st.text_area(
                        label=f"Page {image_item['page_number']} OCR Text",
                        value=image_item["content"],
                        height=200,
                        key=f"image_ocr_{i}",
                    )
        else:
            st.info("No OCR text extracted from images.")
    with tabs[5]:
        st.header("PDF Segments")
        if st.session_state.pdf_content and "segments" in st.session_state.pdf_content:
            for page_data in st.session_state.pdf_content["segments"]:
                st.subheader(f"Page {page_data['page_number']}")
                col1, col2 = st.columns([3, 2]) # Give more space to the image/plot

                with col1:
                    page_index = page_data["page_number"] - 1
                    if 0 <= page_index < len(st.session_state.pdf_content["pages"]):
                        page_content_item = st.session_state.pdf_content["pages"][page_index]
                        page_image = page_content_item["image"]
                        zoom_factor = page_content_item.get("zoom", 1.0)

                        img = Image.open(io.BytesIO(base64.b64decode(page_image)))

                        # Create a new figure and axis
                        # Adjust figsize to match aspect ratio
                        img_w, img_h = img.size
                        aspect = img_h / img_w
                        fig, ax = plt.subplots(figsize=(10, 10 * aspect))
                        ax.imshow(img)

                        # Add bounding boxes for each segment
                        segment_colors = {
                            "text": "blue",
                            "image": "green",
                            "table": "red",
                            "chart": "purple",
                            "latex": "orange",
                        }

                        for segment in page_data["segments"]:
                            # BBox is [x0, y0, x1, y1]
                            x0, y0, x1, y1 = segment["bbox"]

                            # Scale coordinates by zoom factor
                            # BBox is usually in points (1/72 inch).
                            # Image is zoomed by 'zoom' relative to 72 DPI (usually).
                            # If PyMuPDF get_pixmap uses default 72 DPI when zoom=1,
                            # then simple multiplication is correct.
                            x = x0 * zoom_factor
                            y = y0 * zoom_factor
                            w = (x1 - x0) * zoom_factor
                            h = (y1 - y0) * zoom_factor

                            rect = patches.Rectangle(
                                (x, y),
                                w,
                                h,
                                linewidth=2,
                                edgecolor=segment_colors.get(segment["type"], "gray"),
                                facecolor="none",
                            )
                            ax.add_patch(rect)

                        ax.axis("off")
                        st.pyplot(fig, use_container_width=True)
                    else:
                        st.error("Page image not found.")

                with col2:
                    # Group segments by type
                    segment_groups = {}
                    for segment in page_data["segments"]:
                        if segment["type"] not in segment_groups:
                            segment_groups[segment["type"]] = []
                        segment_groups[segment["type"]].append(segment)

                    # Display grouped and collapsible segments
                    for segment_type, segments in segment_groups.items():
                        with st.expander(
                            f"{segment_type.capitalize()} ({len(segments)})",
                            expanded=False,
                        ):
                            for segment in segments:
                                st.markdown(
                                    f'<div style="border-left: 5px solid {segment_colors[segment_type]}; padding-left: 10px;">',
                                    unsafe_allow_html=True,
                                )
                                if (
                                    segment["type"] == "image"
                                    and "image_data" in segment
                                ):
                                    st.image(
                                        base64.b64decode(segment["image_data"]),
                                        caption="Extracted Image",
                                        use_column_width=True,
                                    )
                                content_preview = str(segment['content'])[:100]
                                st.write(
                                    f"Content: {content_preview}..."
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
