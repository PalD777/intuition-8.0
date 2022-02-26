var fireBase = fireBase || firebase;
var hasInit = false;
var config = {
  apiKey: "AIzaSyCd39FhWmPH1bdj4zKUr7J96HkhEObTuTI",
  authDomain: "nft-finex.firebaseapp.com",
  projectId: "nft-finex",
  storageBucket: "nft-finex.appspot.com",
  messagingSenderId: "389391286138",
  appId: "1:389391286138:web:42d3960ecf296fc06e60c3",
  measurementId: "G-JC3GTCC14E"
};
if (!hasInit) {
  firebase.initializeApp(config);
  hasInit = true;
}
