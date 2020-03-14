## Grin-Pool User Interface

The purpose of this repo is to provide a web user interface for a GRIN mining pool. More information can be found [here](https://github.com/grin-pool/grin-pool)

### Installation & Deployment

In order to build and deploy the web-ui, we are going to need to install a few Javascript-related items:

***node**: allows command-line execution of Javascript | [installation instructions](https://nodejs.org/en/download/package-manager/)  
***yarn**: Javascript dependency manager | [instructions](https://yarnpkg.com/lang/en/docs/install/)  
***serve**: allows serving of local files. `yarn global serve` from the command line | [more info](https://www.npmjs.com/package/serve)  

#### Steps to build & serve:
1.) From your terminal, navigate to the `grin-pool/grin-py/webui-js` file  
2.) Execute `yarn` from the command line  
3.) Execute `yarn start` to serve development version  

*The next two steps are only for generating and serving production builds*  

4.) Execute `yarn build` to create a production build (which will be generated in the `/build` folder  
5.) Execute `serve -s` to serve the production version to port `5000`. To change the port number you can execute the command `yarn serve -s build -p [portNumber]` 
