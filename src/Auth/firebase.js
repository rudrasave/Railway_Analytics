// Firebase configuration and initialization
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getAnalytics } from 'firebase/analytics';

const firebaseConfig = {
  apiKey: 'AIzaSyA72gq_ZZm6mx4Hrk_d0hkwsLodNENDC9U',
  authDomain: 'railanalytics-ca775.firebaseapp.com',
  projectId: 'railanalytics-ca775',
  storageBucket: 'railanalytics-ca775.appspot.com',
  messagingSenderId: '726414815728',
  appId: '1:726414815728:web:fea123f8757874cf88ed35',
  measurementId: 'G-4C31W6PXN8'
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app);

export { auth, analytics };