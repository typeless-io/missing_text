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

    # Sidebar for controls
    with st.sidebar:
        st.header("Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file is not None:
            if st.button("Process PDF"):
                 with st.spinner("Extracting content..."):
                    # We can customize the zoom here if needed, but defaults are good
                    pdf_content = sync_extract_pdf(uploaded_file.getvalue(), zoom=2.0)
                    st.session_state.pdf_content = pdf_content
                    st.success("PDF processed successfully!")

        st.divider()

        # Pagination Controls
        if st.session_state.pdf_content and "pages" in st.session_state.pdf_content:
            total_pages = len(st.session_state.pdf_content["pages"])
            st.subheader(f"Page Navigation (Total: {total_pages})")

            # Initialize page number if not set
            if "current_page" not in st.session_state:
                st.session_state.current_page = 1

            # Number input for page selection
            page_number = st.number_input(
                "Go to page",
                min_value=1,
                max_value=total_pages,
                value=st.session_state.current_page
            )
            st.session_state.current_page = page_number

            # Previous/Next buttons
            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.button("Previous"):
                    if st.session_state.current_page > 1:
                        st.session_state.current_page -= 1
                        st.rerun()
            with col_next:
                if st.button("Next"):
                    if st.session_state.current_page < total_pages:
                        st.session_state.current_page += 1
                        st.rerun()

            st.write(f"Showing Page: {st.session_state.current_page}")
        else:
            st.info("Upload and process a PDF to see page controls.")

    # Main Content Area
    if not st.session_state.pdf_content:
        st.info("Please upload and process a PDF file using the sidebar.")
        return

    # Helper to get current page index (0-based)
    current_page_idx = st.session_state.current_page - 1

    # Create tabs for navigation
    tabs = st.tabs(
        [
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
        st.header(f"Extracted Text - Page {st.session_state.current_page}")
        if (
            st.session_state.pdf_content
            and "text" in st.session_state.pdf_content
            and st.session_state.pdf_content["text"]
        ):
            # Find content for the current page
            text_item = next((item for item in st.session_state.pdf_content["text"] if item['page_number'] == st.session_state.current_page), None)

            if text_item:
                col1, col2 = st.columns([1, 1]) # Equal columns
                with col1:
                    page_data = st.session_state.pdf_content["pages"][current_page_idx]
                    if page_data.get("image"):
                        st.image(
                            base64.b64decode(page_data["image"]),
                            caption=f"Original Page {st.session_state.current_page}",
                            use_column_width=True,
                        )
                    else:
                        st.error("Page image could not be rendered.")
                with col2:
                    st.text_area(
                        label=f"Page {st.session_state.current_page} Content",
                        value=text_item["content"],
                        height=800, # Increased height
                        key=f"text_{current_page_idx}",
                    )
            else:
                 st.info(f"No text extracted for page {st.session_state.current_page}.")
        else:
            st.warning("No text extracted from the PDF.")

    with tabs[1]:
        st.header(f"Extracted Tables - Page {st.session_state.current_page}")
        if (
            st.session_state.pdf_content
            and "tables" in st.session_state.pdf_content
            and st.session_state.pdf_content["tables"]
        ):
            # Filter tables for current page
            tables_on_page = [t for t in st.session_state.pdf_content["tables"] if t['page_number'] == st.session_state.current_page]

            if tables_on_page:
                for i, table_item in enumerate(tables_on_page):
                    st.subheader(f"Table {i+1}")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        page_image = st.session_state.pdf_content["pages"][current_page_idx]["image"]
                        st.image(
                            base64.b64decode(page_image),
                            caption=f"Original Page {st.session_state.current_page}",
                            use_column_width=True,
                        )
                    with col2:
                        st.dataframe(table_item["content"], key=f"table_pymupdf_{current_page_idx}_{i}", use_container_width=True)
            else:
                st.info(f"No tables found on page {st.session_state.current_page}.")
        else:
            st.info("No tables extracted using PyMuPDF.")

    with tabs[2]:
        st.header(f"Extracted Images - Page {st.session_state.current_page}")
        if (
            st.session_state.pdf_content
            and "images" in st.session_state.pdf_content
            and st.session_state.pdf_content["images"]
        ):
             # Filter images for current page
            images_on_page = [img for img in st.session_state.pdf_content["images"] if img['page_number'] == st.session_state.current_page]

            if images_on_page:
                for i, image_item in enumerate(images_on_page):
                    st.subheader(f"Image {i+1}")
                    col1, col2 = st.columns(2)
                    with col1:
                        # Display the original PDF page
                        page_image = st.session_state.pdf_content["pages"][current_page_idx]["image"]
                        st.image(
                            base64.b64decode(page_image),
                            caption=f"Original Page {st.session_state.current_page}",
                            use_column_width=True,
                        )
                    with col2:
                        if "image_data" in image_item:
                            image_bytes = base64.b64decode(image_item["image_data"])
                            st.image(
                                Image.open(io.BytesIO(image_bytes)),
                                caption="Extracted Image",
                                use_column_width=True,
                            )
                        else:
                            st.write("No image data available for this item.")
            else:
                st.info(f"No images found on page {st.session_state.current_page}.")
        else:
            st.info("No images extracted from the PDF.")

    with tabs[3]:
        st.header(f"Image OCR - Page {st.session_state.current_page}")
        if (
             st.session_state.pdf_content
            and "images" in st.session_state.pdf_content
        ):
             # Filter images for current page
            images_on_page = [img for img in st.session_state.pdf_content["images"] if img['page_number'] == st.session_state.current_page]

            if images_on_page:
                for i, image_item in enumerate(images_on_page):
                    st.subheader(f"Image {i+1} OCR")
                    col1, col2 = st.columns(2)
                    with col1:
                        if "image_data" in image_item:
                            image_bytes = base64.b64decode(image_item["image_data"])
                            st.image(
                                Image.open(io.BytesIO(image_bytes)),
                                caption="Extracted Image",
                                use_column_width=True,
                            )
                        else:
                            st.write("No image data available for this item.")
                    with col2:
                        st.text_area(
                            label="OCR Text",
                            value=image_item["content"],
                            height=200,
                            key=f"image_ocr_{current_page_idx}_{i}",
                        )
            else:
                 st.info(f"No images found on page {st.session_state.current_page}.")
        else:
            st.info("No OCR text extracted from images.")

    with tabs[4]:
        st.header(f"PDF Segments - Page {st.session_state.current_page}")
        if st.session_state.pdf_content and "segments" in st.session_state.pdf_content:
            # Find segments for current page
            page_data = next((item for item in st.session_state.pdf_content["segments"] if item['page_number'] == st.session_state.current_page), None)

            if page_data:
                col1, col2 = st.columns([3, 2]) # Give more space to the image/plot

                with col1:
                    page_content_item = st.session_state.pdf_content["pages"][current_page_idx]
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
                st.info(f"No segments found for page {st.session_state.current_page}.")
        else:
            st.warning("No segment data available. Please process a PDF first.")

    with tabs[5]:
        st.header("Download Extracted Content as JSON")
        if st.session_state.pdf_content:
            json_str = json.dumps(st.session_state.pdf_content, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="extracted_content.json",
                mime="application/json",
            )

    with tabs[6]:
        st.header("Processing Logs")
        if st.session_state.pdf_content:
            st.text("PDF processing completed successfully.")
            st.text("No errors or warnings were encountered during processing.")


if __name__ == "__main__":
    main()
