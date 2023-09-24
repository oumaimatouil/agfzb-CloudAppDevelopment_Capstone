const http = require('http');
const url = require('url');
const Cloudant = require('@cloudant/cloudant');

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
    const parsedUrl = url.parse(req.url, true);
    const { pathname, query } = parsedUrl;

    if (pathname === '/api/dealership' && req.method === 'GET') {
        // Return all dealerships without any specific query
        db.list({ include_docs: true }, (err, body) => {
            if (err) {
                console.error('Error fetching dealerships:', err);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'An error occurred while fetching dealerships.' }));
            } else {
                const dealerships = body.rows.map(row => row.doc);
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify(dealerships));
            }
        });
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

const port = process.env.PORT || 3000;

// Start the server
server.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
