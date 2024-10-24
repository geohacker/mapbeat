const AWS = require('aws-sdk');

// In-memory storage of connections (will be cleared on Lambda cold starts)
let connections = new Set();

const s3 = new AWS.S3();
const bucketName = 'real-changesets';

const getChangeset = async (key) => {
    return new Promise((resolve, reject) => {
        console.log('bucketName', bucketName)
        console.log('key', key);
        s3.getObject({ Bucket: bucketName, Key: key }, (err, data) => {
            if (err) {
              console.error("Error fetching the file: ", err);
              reject(err);
            }

            try {
              const jsonData = JSON.parse(data.Body.toString('utf-8'));
              console.log("JSON data:", jsonData);
              resolve(jsonData)
            } catch (parseError) {
              console.error("Error parsing JSON: ", parseError);
              reject(parseError);
            }
          });
    })
}

exports.handler = async (event) => {
    // Set up API Gateway client - endpoint will be set via environment variable
    const api = new AWS.ApiGatewayManagementApi({
        endpoint: process.env.WEBSOCKET_API_ENDPOINT
    });
    
    if (event.Records) {  // SNS message
        const message = JSON.parse(event.Records[0].Sns.Message);
        console.log('message', message)
        // Broadcast to all connected clients
        const disconnectedClients = [];
        
        const key = message['Records'][0]['s3']['object']['key']
        console.log(key)
        const changeset = await getChangeset(key)

        await Promise.all([...connections].map(async (connectionId) => {
            try {
                await api.postToConnection({
                    ConnectionId: connectionId,
                    Data: JSON.stringify(changeset['metadata'])
                }).promise();
            } catch (e) {
                if (e.statusCode === 410) {
                    // Remove stale connections
                    disconnectedClients.push(connectionId);
                }
            }
        }));
        
        // Clean up disconnected clients
        disconnectedClients.forEach(connectionId => connections.delete(connectionId));
        
    } else {  // WebSocket connection
        const connectionId = event.requestContext.connectionId;
        
        if (event.requestContext.routeKey === '$connect') {
            connections.add(connectionId);
        } else if (event.requestContext.routeKey === '$disconnect') {
            connections.delete(connectionId);
        }
    }
    
    return { statusCode: 200, body: 'OK' };
}