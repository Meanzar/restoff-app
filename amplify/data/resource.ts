import { type ClientSchema, a, defineData } from "@aws-amplify/backend";

/*== STEP 1 ===============================================================
The section below creates a Todo database table with a "content" field. Try
adding a new "isDone" field as a boolean. The authorization rule below
specifies that any user authenticated via an API key can "create", "read",
"update", and "delete" any "Todo" records.
=========================================================================*/
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
    if (!secretResponse.SecretString) {
      throw new Error("SecretString is undefined");
    }
    const apiKey = JSON.parse(secretResponse.SecretString).apiKey;

    // Fetch data from API
    const apiResponse = await fetch("https://api.yelp.com/v3/businesses/search", {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    const data = await apiResponse.json() as { id: string }; // Add type assertion
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
    const errorMessage = (error as Error).message;
    return { statusCode: 500, body: `Error: ${errorMessage}` };
  }
};


/*== STEP 2 ===============================================================
Go to your frontend source code. From your client-side code, generate a
Data client to make CRUDL requests to your table. (THIS SNIPPET WILL ONLY
WORK IN THE FRONTEND CODE FILE.)

Using JavaScript or Next.js React Server Components, Middleware, Server 
Actions or Pages Router? Review how to generate Data clients for those use
cases: https://docs.amplify.aws/gen2/build-a-backend/data/connect-to-API/
=========================================================================*/

/*
"use client"
import { generateClient } from "aws-amplify/data";
import type { Schema } from "@/amplify/data/resource";

const client = generateClient<Schema>() // use this Data client for CRUDL requests
*/

/*== STEP 3 ===============================================================
Fetch records from the database and use them in your frontend component.
(THIS SNIPPET WILL ONLY WORK IN THE FRONTEND CODE FILE.)
=========================================================================*/

/* For example, in a React component, you can use this snippet in your
  function's RETURN statement */
// const { data: todos } = await client.models.Todo.list()

// return <ul>{todos.map(todo => <li key={todo.id}>{todo.content}</li>)}</ul>
