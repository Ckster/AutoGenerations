// Import the express library
const express = require('express')
const fetch = require("node-fetch");
const hbs = require("hbs");

// Create a new express application
const app = express();
app.set("view engine", "hbs")
app.set("views", `${process.cwd()}/views`);

// Send a "Hello World!" response to a default get request
app.get('/', async (req, res) => {
    res.render("index");
})

// Send a JSON response to a default get request
app.get('/ping', async (req, res) => {
    const requestOptions = {
        'method': 'GET',
        'headers': {
            'x-api-key': 'wix41uv8dhpnbi9n7gaq948s',
        },
    };

    const response = await fetch(
        'https://api.etsy.com/v3/application/openapi-ping',
        requestOptions
    );

    if (response.ok) {
        const data = await response.json();
        res.send(data);
    } else {
        res.send("oops");
    }
});

const clientID = 'wix41uv8dhpnbi9n7gaq948s';
const clientVerifier = 'o2qYNZeg1ZZFaPQq6bdBeoGsJw3WBF9-OHerUF6vf7w';
const redirectUri = 'http://localhost:3003/oauth/redirect';

app.get('/refresh_token', async (req, res) => {
    const tokenUrl = 'https://api.etsy.com/v3/public/oauth/token';
    const requestOptions = {
        method: 'POST',
        body: JSON.stringify({
            grant_type: 'refresh_token',
            client_id: clientID,
            refresh_token: '695701628.B3fUHRa8rRsWaSkpHoPr7dGSEdJ_o_gvsPOTbtnX9SKfUwG9G_2wJYKBsRqpW6GbJnyHNCxPEpSuFBSjgr1xojXufa'
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const response = await fetch(tokenUrl, requestOptions);

    // Extract the access token from the response access_token data field
    if (response.ok) {
        const tokenData = await response.json();
        res.send(tokenData);
    } else {
        res.send(response.json());
    }

})

app.get("/oauth/redirect", async (req, res) => {
    // The req.query object has the query params that Etsy authentication sends
    // to this route. The authorization code is in the `code` param
    const authCode = req.query.code;
    console.log(authCode);
    console.log(req);
    console.log(req.query);

    console.log()
    const tokenUrl = 'https://api.etsy.com/v3/public/oauth/token';
    const requestOptions = {
        method: 'POST',
        body: JSON.stringify({
            grant_type: 'authorization_code',
            client_id: clientID,
            redirect_uri: redirectUri,
            code: authCode,
            code_verifier: clientVerifier,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const response = await fetch(tokenUrl, requestOptions);

    // Extract the access token from the response access_token data field
    if (response.ok) {
        const tokenData = await response.json();
        res.send(tokenData);
    } else {
        res.send(response.json());
    }
});

// Start the server on port 3003
const port = 3003
app.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`)
})
