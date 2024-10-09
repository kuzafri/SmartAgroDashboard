// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { VueFire, VueFireFirestoreOptionsAPI } from "vuefire";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyC_6j_THdOW4aGtwfGX5rWDqRj2pmti3-c",
  authDomain: "finalyearproject-c3415.firebaseapp.com",
  projectId: "finalyearproject-c3415",
  storageBucket: "finalyearproject-c3415.appspot.com",
  messagingSenderId: "285332282300",
  appId: "1:285332282300:web:ff0c4817dc936f1ac8e9b9",
  measurementId: "G-XF2KHFNDDV"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);