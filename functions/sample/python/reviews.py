"""
Module: reviews.py

This module defines a Flask application for managing dealership reviews using Cloudant.
"""

from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from flask import Flask, jsonify, request, abort

# Add your Cloudant service credentials here
CLOUDANT_USERNAME = 'fa7eeb90-af89-4edb-84d5-37062403e29e-bluemix'
CLOUDANT_API_KEY = 'fY-Ejcu2K9AeIKC2HcyITpNW5cO2CNiwJx78I_UMaDE6'
CLOUDANT_URL = (
    'https://fa7eeb90-af89-4edb-84d5-37062403e29e-'
    'bluemix.cloudantnosqldb.appdomain.cloud'
)

# Initialize the Cloudant client
authenticator = IAMAuthenticator(CLOUDANT_API_KEY)
service = CloudantV1(authenticator=authenticator)
service.set_service_url(CLOUDANT_URL)

app = Flask(__name__)

@app.route('/api/get_reviews', methods=['GET'])
def get_reviews():
    """
    Get reviews for a dealership.

    Returns:
        JSON response containing review data.
    """
    dealership_id = request.args.get('id')

    # Check if "id" parameter is missing
    if dealership_id is None:
        return jsonify({"error": "Missing 'id' parameter in the URL"}), 400

    # Convert the "id" parameter to an integer (assuming "id" should be an integer)
    try:
        dealership_id = int(dealership_id)
    except ValueError:
        return jsonify({"error": "'id' parameter must be an integer"}), 400

    # Define the query based on the 'dealership' ID
    selector = {
        'dealership': dealership_id
    }

    # Execute the query using the find method
    result = service.post_find(
        db='reviews',
        selector=selector,
    ).get_result()

    # Create a list to store the documents
    data_list = result['docs']

    # Return the data as JSON
    return jsonify(data_list)

@app.route('/api/post_review', methods=['POST'])
def post_review():
    """
    Post a review for a dealership.

    Returns:
        JSON response indicating success or error.
    """
    if not request.json:
        abort(400, description='Invalid JSON data')

    # Extract review data from the request JSON
    review_data = request.json

    # Validate that the required fields are present in the review data
    required_fields = ['name', 'dealership', 'review',
    'purchase', 'purchase_date', 'car_make', 'car_model', 'car_year']
    for field in required_fields:
        if field not in review_data:
            abort(400, description=f'Missing required field: {field}')

    # Save the review data as a new document in the Cloudant database
    service.post_document(
        db='reviews',
        document=review_data,
    )

    return jsonify({"message": "Review posted successfully"}), 201

if __name__ == '__main__':
    app.run(debug=True)
