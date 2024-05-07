from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from ping3 import ping, verbose_ping
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
  # Initialize the WebDriver
@st.cache_resource
def get_driver():
    return webdriver.Chrome(
        service=Service(
            ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()
        ),
        options=options,
    )

options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--headless")
driver = get_driver()



def login(name,passw):

     
       # Open the website
       driver.get('https://lukoilmutabakat.com:14401/Account')
       st.write("Lukoil Portalına bağlanıldı.")

       # Find the login form elements and enter your credentials
       username = driver.find_element_by_name('Kod')
       username.send_keys(name)
       password = driver.find_element_by_name('Sifre')
       password.send_keys(passw)
       login_button = driver.find_element_by_xpath("//*[contains(text(), 'Giriş')]")
       login_button.click()

       # Wait for the page to load
       time.sleep(2)

       # Navigate to the page you want to scrape
       driver.get('https://lukoilmutabakat.com:14401/BayiList?OnlineDurumId=0')
       time.sleep(2)
       st.write("Lukoil Portalına giriş yapıldı.")
       # Now you can scrape the data from the page
       # For example, you can find an element by its ID and get its text
       data_element = driver.find_element_by_id('dvBayiList_grid')
       text_data = data_element.text
       #print(data_element.text)
       driver.close()
       st.write("Portaldan Offline istasyon verileri çekildi.")
       return text_data


def prepareData(text_data):
       data = []
       lines = text_data.strip().split('\n')
       columns = ['Ad' , 'No' , 'Ip']
       for line in lines:
           values = [value.strip() for value in line.split('Aktif')]
           data.append(dict(zip(columns, values)))


       df = pd.DataFrame(data)
       NoColumn = []
       IpColumn = []
       AdColumn = []




       for idx,x in enumerate(df['Ad']):
           if idx % 3 == 0:
               df['No'][idx] ='BAY' + df['No'][idx].split('BAY')[1]
               NoColumn.append(df['No'][idx])
           if idx % 3 == 2:
               df['Ad'][idx] ='10.' + df['Ad'][idx].split('10.')[1]
               IpColumn.append(df['Ad'][idx])
           if idx % 3 == 1:
               AdColumn.append(df['Ad'][idx])

       df = pd.DataFrame(columns=['Lisansno','Bayi Ünvan','Ip Adres'])
       df['Bayi Ünvan'] = AdColumn
       df['Ip Adres'] = IpColumn
       df['Lisansno'] = NoColumn
       st.write("Veriler ping atmak için hazırlandı.")
       return(df)


def pingNow(df):
     ModemYok = []
     ModemVarPcYok = []
     ErisimVar = []
     for x, ip in enumerate(df["Ip Adres"]):
         st.write(df["Bayi Ünvan"][x] + " kontrol ediliyor.")
         if (ping(ip) == None):
             if (ping(ip.rstrip("0")) == None):
                 ModemYok.append([df["Lisansno"][x], df["Bayi Ünvan"][x], ip])
             else:
                 ModemVarPcYok.append([df["Lisansno"][x], df["Bayi Ünvan"][x], ip])
         else:
             ErisimVar.append([df["Lisansno"][x], df["Bayi Ünvan"][x], ip])

     data2 = {
         'Modeme Erişim Yok': ModemYok,
         "Modeme Erişim Var, Bilgisayara Yok": ModemVarPcYok,
         "Bilgisayara Erişim Var": ErisimVar
     }
     return data2



# Close the WebDriver

st.title('Lukoil Portalı Offline İstasyonlar Kontrol')
kadi = st.text_input("Kullanıcı Adı", "")
Sifre = st.text_input("Parola", "", type="password")
if st.button("Giriş Yap"):
    a = login(kadi,Sifre)
    b = prepareData(a)
    c = pingNow(b)
    st.subheader('Modeme Erişim Yok')
    for a in c['Modeme Erişim Yok']:
       st.write("%s     %s     %s"  % (a[0] , a[1] , a[2]))
    st.subheader("Modeme Erişim Var, Bilgisayara Yok")
    for a in c["Modeme Erişim Var, Bilgisayara Yok"]:
       st.write("%s     %s     %s"  % (a[0] , a[1] , a[2]))
    st.subheader("Bilgisayara Erişim Var")
    for a in c["Bilgisayara Erişim Var"]:
       st.write("%s     %s     %s"  % (a[0] , a[1] , a[2]))
