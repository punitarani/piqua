
# Piqua
**Quant tools add-on for TD Ameritrade**

_Supports US Equities and Equity Options_




### **Requires TD Ameritrade Developer Account with API Access**

API Guide: https://developer.tdameritrade.com/content/getting-started

Make sure the Redirect URL is set to: https://localhost




## Config file
Create and save the following file in the project's root directory as **config.py**

**DO NOT SHARE THIS FILE OR CONTENTS WITH ANYONE**

    # Config.py

    account_id = r'{account_id}'
    client_id = r'{client_id}'
    redirect_uri = r'https://localhost'

Replace **{account_id}** and **{client_id}** with your account information.

_Account ID is optional but **Client ID is Mandatory**_ 




## Running the program
#### Type the following command from the project's root to run the streamlit app.

    streamlit run main.py

This should open a web browser and display the local-hosted app automatically.

The app can be closed and opened unlimited times as long as the terminal is open.

The url to open the app should also be displayed in the terminal

      You can now view your Streamlit app in your browser.

        Local URL: http://localhost:####
        Network URL: http://###.###.#.##:####

**CAUTION: Anyone connected to the network will be able to access the app with the network url.**

This can be a good thing when running it on a private home network as it will allow you to host it on
one computer and use the app on another computer or a mobile device. In fact, it would be ideal
to host it on a Raspberry Pi to free up CPU and memory usage on your primary device.

However, it can be a security issue running it on a public wifi as it will allow anyone connected to
the same network to access the app with the network url.