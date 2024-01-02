import streamlit as st
import base64
import requests
import json
from streamlit_option_menu import option_menu
import pandas as pd
import webbrowser

st.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)

def downloadImage(key):
    try:
        url = "https://gy7n5q6gjg.execute-api.ap-southeast-1.amazonaws.com/prod/image"
        params = {"key": key}

        response = requests.get(url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json()  # Assuming the response is in JSON format
        else:
            st.write(f"Request failed with status code: {response.status_code}")
            return None
    except Exception as e:
        st.write(f"An error occurred during the request: {e}")
        return None

def convert_epoch_to_time(epoch_time):
    return pd.to_datetime(epoch_time, unit="s")

def main():
    selected = option_menu(
        menu_title="",
        options=["Home","History"],
        icons=["house","clock"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal"
    )

    if selected == "Home":
        st.title("Edit Image")

        col11, col12 = st.columns(2)
        col1, col2, col3 = st.columns([2,1,1])
        
        with col2:
            widthInput = st.number_input("Enter Width:", min_value=10, step=1, value=100)
            grayscale = st.radio("Remove Color:", [True, False], index=1)

            st.write("")
            btn = st.button("Edit Image", type="primary")

        with col3:
            heightInput = st.number_input("Enter Height:", min_value=10, step=1, value=100)
            crop = st.radio("Crop Image", [True, False], index=0)

            
        with col12:
            quality = st.slider("Image Quality:", min_value=1, max_value=100, value=100, step=1)
            type = st.radio("Save Image As:", ["png", "jpg","jpeg","original"], index=3, horizontal=True)
            

        
        uploaded_file = col11.file_uploader("", type=["jpg", "jpeg", "png"])
        

        if uploaded_file is not None:
            

            col1.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
            
            if btn:
                with st.spinner("Editting..."):
                    url = "https://gy7n5q6gjg.execute-api.ap-southeast-1.amazonaws.com/prod/image"
                    base64_data = base64.b64encode(uploaded_file.read()).decode("utf-8")
                    fileName =  uploaded_file.name
                    if type == "original":
                        type = uploaded_file.type.split("/")[1]
                        contentType= uploaded_file.type
                    else:   
                        contentType = "image/" + type

                    params={
                        "width" : widthInput,
                        "height": heightInput,
                        "grayscale":grayscale,
                        "quality":quality,
                        "crop":crop,
                        "type":type
                    }
                    data = {
                        "name":fileName,
                        "type":contentType,
                        "file":base64_data
                    }

                    response = requests.post(url, params=params, data=json.dumps(data))
                st.write("Status Code:", response.status_code)
                if(response.status_code==200):
                    url = json.loads(response.text)["url"]
                    st.write(f"<a href='{url}' target='_blank'>Click here to see the image!</a>", unsafe_allow_html=True)

    if selected == "History":
        st.title("Image History")
        url = "https://gy7n5q6gjg.execute-api.ap-southeast-1.amazonaws.com/prod/images"
        response = requests.get(url)
        if response.status_code == 200:
            # df = pd.DataFrame(response.json())
            data = (response.json().get("items", []))
            df = pd.DataFrame(data)
            #
            df["size"] = df["width"].astype(str) + "x" + df["height"].astype(str)
            df["created_at"] = convert_epoch_to_time(df["created_at"])

            # Arrange column names in a specific order (modify as needed)
            column_order = ["name", "size", "ContentType","grayscale", "created_at"]
            col1, col2, col3, col4, col5, col6 = st.columns([5,2,2,2,3,2])
            with col1:
                st.write("Name")
            with col2:
                st.write("Size")
            with col3:
                st.write("Type")
            with col4:
                st.write("Grayscale")
            with col5:
                st.write("Created_at")
            with col6:
                st.write("Download")

            for index, row in df.iterrows():
                col1, col2, col3, col4, col5, col6 = st.columns([5,2,2,2,3,2])
                with col1:
                    st.write(row["name"])
                with col2:
                    st.write(row["size"])
                with col3:
                    row["ContentType"].startswith("image/")
                    st.write(row["ContentType"][len("image/"):])
                with col4:
                    st.write(row["grayscale"])
                with col5:
                    st.write(row["created_at"])
                with col6:
                    btn = st.button("⬇", key=index)
                    if btn:
                        url = downloadImage(row["name"])["url"]
                        webbrowser.open_new_tab(url)

            

        else:
            st.error(f"Error retrieving data. Status code: {response.status_code}")
            return None

if __name__ == "__main__":
    main()


