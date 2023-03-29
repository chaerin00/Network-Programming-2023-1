from geopy.geocoders import Nominatim

if __name__ == '__main__':
    address = "Sookmyung women's university"
    user_agent = 'David'
    location = Nominatim(user_agent=user_agent).geocode(address)
    print(location.latitude, location.longitude)
