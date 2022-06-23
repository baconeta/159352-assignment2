# Web Flight Booking System


Made for 159.352 Advanced Web Development at Massey University June 2022 by Joshua Pearson.


## Demo

Run the docker .tar file locally to host the server.
The following docker commands will let you load and run the server from the .tar file

```bash
  docker load -o 20019455.tar.gz
  docker run -it --rm --publish 5555:8000 20019455
```

## Home page

This page has been merged with the booking page in order to direct a new customer straight to the page where they can search for available flights.
There are links across the top of the page for navigation and user management which adapt automatically to the logged in status.

![image](https://user-images.githubusercontent.com/36744690/175245961-be34398c-3a8e-4575-93e7-c6d3cfc208c3.png)


## Booking page

On this page, a user can find flights matching their filled criteria:
![image](https://user-images.githubusercontent.com/36744690/175246183-65182104-7c0c-4c56-8a84-81fac4561901.png)

This data is pulled from the database, validated and sent to the server when the form is submitted.

![image](https://user-images.githubusercontent.com/36744690/175246490-fe82edc5-2692-4c50-9a0d-79d1135a4cd7.png)

Search results are shown allowing users to see 3 days either side of their selected date making it easier to find a matching flight overall.


Selecting 'Book this flight' takes the user to a confirmation page. Once they click confirm booking, the data is revalidated to ensure the seats have not been sold in the time the user was scrolling.
![image](https://user-images.githubusercontent.com/36744690/175246800-fd26f0a4-dea4-4f8c-b2e2-43a86b695722.png)

And an invoice page will appear once confirmed:
![image](https://user-images.githubusercontent.com/36744690/175247060-ee42826b-6907-43d3-9b08-ca1fd80ad813.png)

Example invoice:
![image](https://user-images.githubusercontent.com/36744690/175247128-22062b83-7835-41d9-804a-1d794e282c42.png)

## Bonus features

- A fully designed and functioning user registration and login system, which includes password reset functionality and complete validation
- Strong flight validation for stopover flights and simple expansion to add more airports, flights and stopover legs
- Functional from all timezones, no matter where the server is hosted
- Historical bookings system showing all past bookings
- The ability for a logged in user to edit their personal info and update their bookings quickly and easily
- Fully functional HTTPS fucntionality, including protection from cross-site scripting and password leaks with strong hashing authentication
## Tech Stack

- Python 3.10
- Bootstrap JS
- Flask
- WTForms
- Flask-Login
- Bcrypt
- SQLite with FlaskAlchemy

Docker container
- Docker version 20.10.14, build a224086
- Docker Desktop 4.7.1 (77678)


## Acknowledgements and references

- https://www.craiyon.com/ - AI generated logo design
- https://github.com/sparksuite/simple-html-invoice-template - Invoice template
- https://fontawesome.com/ - Various icons by Font Awesome Free
