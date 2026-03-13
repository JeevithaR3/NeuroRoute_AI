import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDaS4Xe0wtqdpwvo3W9-WdR4Fk-z-7ouuw",
  authDomain: "neuro-5c149.firebaseapp.com",
  projectId: "neuro-5c149",
  storageBucket: "neuro-5c149.firebasestorage.app",
  messagingSenderId: "503656664430",
  appId: "1:503656664430:web:3db06a07dcb97082a5c57f",
  measurementId: "G-3CWG9K10Z8",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export default app;
