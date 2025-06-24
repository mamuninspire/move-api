Request url: /api/v1/movers/movers/search/

Request parameters:
	booking_time, booking_type, pickup, dropoff location, vehicle preferences

Response:
	List of available Movers

Algorithm for search:
	1. Get all movers(Mover) who are online, available, rider and then filter by vehicle preferences
	2. From the current location of the movers calculate the distance from the pickup point if its book now
	3. In parallal calculate the distance between pickup and dropoff location using google_map/postgis
	4. estimate the costing for each movers
	5. Return the response

When a customer click "Search Available Rides" button after filling the form:
1. A RideSearch object is created with status "new_search"
2. We see list of available movers based on the search criteria with following information and 
two buttons for each available movers "Send Request" & "Negotiate Price": Driver Name, Rating, estimated cost, mobile no, Car License, make, model and image

3. For each click on "Send Request" button a RideRequestToMover object is created with default comment/message and status is set to 'pending'.
4. And for each click on "Negotiate Price" button a popup will be shown with two form field. i. "Your proposed Price" & ii. Message for custom message and a "Send Request" button. If you click Send Request button a RideRequestToMover object is created with custom message, estimated cost, proposed price and set status to "pending"

5. When customer goes to "Booking Request" page pending tab he will find all pending requests for his rides

6. When customer goes "Booking Request" page accepted tab he will see all accepted request for this ride. When a driver accept a request status for RideSearch and RideRequestToMover changes to accepted. Customer will see confirm button for each accepted request.

7. When customer confirm any request following happens:
	i. Status change for RideSearch to "confirmed"
	ii. All RideRequestToMover for RideSearch other than the confirmed RideRequestToMover will change status to "rejected"
	iii. RideRequestToMover status change to "confirmed"
	iv. A Ride object is created for the confirmed RideRequestToMover and Ride status set to "confirmed"
	v. Also it creates a Booking object for the Ride


Request URL: /api/v1/booking/send-request/

Request parameters:
    ride_search, mover, estimated_cost, proposed_cost, agreed_price 

Response: status = pending, 