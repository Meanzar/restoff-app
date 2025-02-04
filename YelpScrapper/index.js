const axios = require('axios');

// Replace 'YOUR_API_KEY' with your actual Yelp API key
const apiKey = 'APIKEY';

// Function to search for restaurants in Paris
async function searchRestaurants() {
  const url = 'https://api.yelp.com/v3/businesses/search';
  const params = {
    location: 'Paris',
    categories: 'restaurants',
    limit: 10, // Number of results to retrieve
  };

  try {
    const response = await axios.get(url, {
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
      params,
    });

    const businesses = response.data.businesses;
    businesses.forEach((business, index) => {
      console.log(`${index + 1}. ${business.name}`);
      console.log('---');
    });
  } catch (error) {
    console.error('Error fetching data from Yelp API:', error.message);
  }
}

searchRestaurants();
