from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Session
import sqlalchemy.orm
from sqlalchemy.ext.declarative import declarative_base

Base = sqlalchemy.orm.declarative_base()

class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    reviews = relationship('Review', back_populates='restaurant', cascade='all, delete-orphan')

    @classmethod
    def fanciest(cls, session):
        fanciest_restaurant = session.query(cls).order_by(cls.price.desc()).first()
        return f"The fanciest restaurant is {fanciest_restaurant.name} with a price of {fanciest_restaurant.price}."

    def all_reviews(self):
        return [review.full_review() for review in self.reviews]

    def customers(self):
        return [review.customer for review in self.reviews]

    def restaurant_reviews(self):
        return self.reviews
    
    def __repr__(self):
        return f"Customer's favourite restaurant is {self.name} with a price of {self.price}"

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    reviews = relationship('Review', back_populates='customer', cascade='all, delete-orphan')

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def favorite_restaurant(self):
        if not self.reviews:
            return None
        return max(self.reviews, key=lambda review: review.star_rating).restaurant

    def add_review(self, restaurant, rating):
        review = Review(restaurant=restaurant, customer=self, star_rating=rating)
        self.reviews.append(review)

    def delete_reviews(self, restaurant, session):
        reviews_to_delete = [review for review in self.reviews if review.restaurant == restaurant]

        for review in reviews_to_delete:
            existing_review = session.query(Review).get(review.id)
            if existing_review is not None:
                session.delete(existing_review)

            # Remove the review from the lists based on its id
            self.reviews = [r for r in self.reviews if r.id != review.id]
            restaurant.reviews = [r for r in restaurant.reviews if r.id != review.id]

        session.commit()

    def customer_reviews(self):
        return self.reviews

    def reviewed_restaurants(self):
        return [review.restaurant for review in self.reviews]

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    star_rating = Column(Integer)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    restaurant = relationship('Restaurant', back_populates='reviews')
    customer = relationship('Customer', back_populates='reviews')

    def full_review(self):
        return f"Review for {self.restaurant.name} by {self.customer.full_name()}: {self.star_rating} stars."

# Create an SQLite database in memory for testing
engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)

# Create a session
session = Session(engine)

# Sample data
restaurant1 = Restaurant(name='Best Food Place', price=3)
restaurant2 = Restaurant(name='Sarova Skies', price=4)

customer1 = Customer(first_name='John', last_name='Doe')
customer2 = Customer(first_name='Jane', last_name='Smith')

review1 = Review(restaurant=restaurant1, customer=customer1, star_rating=5)
review2 = Review(restaurant=restaurant2, customer=customer2, star_rating=4)
review3 = Review(restaurant=restaurant2, customer=customer1, star_rating=3)

# Add objects to the session
session.add_all([restaurant1, restaurant2, customer1, customer2, review1, review2])

# Commit the session to the database
session.commit()
# Print all customers
all_customers = session.query(Customer).all()
print("\nAll Customers:")
for customer in all_customers:
    print(f"{customer.full_name()}")



# Print all reviews
all_reviews = session.query(Review).all()
print("\nAll Reviews:")
for review in all_reviews:
    print(f"{review.full_review()}")



# Print all restaurants
all_restaurants = session.query(Restaurant).all()
print("\nAll Restaurants:")
for restaurant in all_restaurants:
    print(f"{restaurant.name}, Price: {restaurant.price}")



# Display restaurant information
print("\nDisplay restaurant information:")
print(f"\nRestaurant: {restaurant1.name}, Price: {restaurant1.price}")
print("Reviews for the restaurant:")
for review in restaurant1.reviews:
    print(f"- {review.full_review()}\n")

print(f"\nRestaurant: {restaurant2.name}, Price: {restaurant2.price}")
print("Reviews for the restaurant:")
for review in restaurant2.reviews:
    print(f"- {review.full_review()}")



# Display customer information
print("Display customer information:")
print(f"\nCustomer: {customer1.full_name()}")
print(customer1.favorite_restaurant())
print("Reviews by the customer:")
for review in customer1.reviews:
    print(f"- {review.full_review()}\n")

print(f"\nCustomer: {customer2.full_name()}")
print(customer2.favorite_restaurant())
print("Reviews by the customer:")
for review in customer2.reviews:
    print(f"- {review.full_review()}")



# Display information about the first review
print("Display information about the first review:")
first_review = session.query(Review).first()
print(f"\nReview: {first_review.full_review()}")
print(f"Restaurant: {first_review.restaurant.name}")
print(f"Customer: {first_review.customer.full_name()}\n")



# Fanciest restaurant
print(Restaurant.fanciest(session))


# Adding and deleting a review
print("Adding a Review:")
customer2.add_review(restaurant1, 3)
print(customer2.reviews[1].full_review())



print("\nBefore Deleting Review:")
print(restaurant1.all_reviews())

print("\nAfter Deleting Review:")
customer2.delete_reviews(restaurant1, session)  
print(restaurant1.all_reviews())