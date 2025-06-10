import streamlit as st                                                       
                                                                                
redirect_url = "https://kamoyan-seatassign.fly.dev"                                 
                                                                                
# リダイレクトさせるためのHTML埋め込み                                       
st.markdown(f"""                                                             
    <html>                                                                   
        <head>                                                               
            <meta http-equiv="refresh" content="0; url={redirect_url}">      
        </head>                                                              
        <body>                                                               
            <p>Redirecting...</p>                                            
        </body>                                                              
    </html>                                                                  
""", unsafe_allow_html=True)