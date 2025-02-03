import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";
import { SecretsManagerClient, GetSecretValueCommand } from "@aws-sdk/client-secrets-manager";
import fetch from "node-fetch";

const region = "eu-north-1";
const dynamoDBClient = new DynamoDBClient({ region });
const secretsManagerClient = new SecretsManagerClient({ region });
const secretName = "apikey";

export const handler = async () => {
  try {
    // Get API key from Secrets Manager
    const secretResponse = await secretsManagerClient.send(new GetSecretValueCommand({ SecretId: secretName }));
    const apiKey = JSON.parse(secretResponse.SecretString).apiKey;

    // Fetch data from API
    const apiResponse = await fetch("https://api.yelp.com/v3/businesses/search", {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    const data = await apiResponse.json();

    // Store in DynamoDB
    const putCommand = new PutItemCommand({
      TableName: "restoff",
      Item: {
        id: { S: data.id }, // Assuming ID is a string
        content: { S: JSON.stringify(data) },
      },
    });

    await dynamoDBClient.send(putCommand);
    
    return { statusCode: 200, body: "Data stored successfully" };
  } catch (error) {
    return { statusCode: 500, body: `Error: ${error.message}` };
  }
};
