const http = require('http');
const url = require('url');
const Cloudant = require('@cloudant/cloudant');
const port = process.env.PORT || 3000;

// Initialize Cloudant connection with IAM authentication
async function dbCloudantConnect() {
    try {
        const cloudant = Cloudant({
            plugins: { iamauth: { iamApiKey: 'fY-Ejcu2K9AeIKC2HcyITpNW5cO2CNiwJx78I_UMaDE6' } }, // Replace with your IAM API key
            url: 'https://fa7eeb90-af89-4edb-84d5-37062403e29e-bluemix.cloudantnosqldb.appdomain.cloud', // Replace with your Cloudant URL
        });

        const db = cloudant.use('dealerships');
        console.info('Connect success! Connected to DB');
        return db;
    } catch (err) {
        console.error('Connect failure: ' + err.message + ' for Cloudant DB');
        throw err;
    }
}

let db;
(async () => {
    db = await dbCloudantConnect();
})();

// Create an HTTP server
const server = http.createServer((req, res) => {
    if (req.method === 'GET' && req.url.startsWith('/api/dealership')) {
        // Parse the URL to extract query parameters
        const parsedUrl = url.parse(req.url, true);
        const { state, id } = parsedUrl.query;

        // Log the received ID for debugging
        console.log('Received request with ID:', id);
        console.log('Received request URL:', req.url);
        console.log('Received request query:', parsedUrl.query);
        // Create a selector object based on query parameters
        const selector = {};
        if (state) {
            selector.state = state;
        }
        if (id) {
            selector.id = parseInt(id);
        }
        const queryOptions = {
            selector,
            // No limit property here
        };
        db.find(queryOptions, (err, body) => {
            if (err) {
                console.error('Error fetching dealerships:', err);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'An error occurred while fetching dealerships.' }));
            } else {
                const dealerships = body.docs;
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(dealerships));
            }
        });
    } else {
        // Handle other routes or invalid routes here
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Route not found.' }));
    }
});

// Start the server
server.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
