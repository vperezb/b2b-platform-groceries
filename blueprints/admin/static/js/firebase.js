const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
_s = urlParams.get('s')
_h = urlParams.get('h')

if (Boolean(_s) & Boolean(_h)){
  redirect_to = '/admin/assign_store_to_user' + window.location.search
}
else{
  redirect_to = '/admin/home'
}

window.addEventListener('load', function () {
  // document.getElementById('sign-out').onclick = function () {
  //   firebase.auth().signOut();
  // };

  // FirebaseUI config.
  var uiConfig = {
    signInSuccessUrl: redirect_to,
    signInOptions: [
      // Comment out any lines corresponding to providers you did not check in
      // the Firebase console.
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID,
      //firebase.auth.FacebookAuthProvider.PROVIDER_ID,
      //firebase.auth.TwitterAuthProvider.PROVIDER_ID,
      //firebase.auth.GithubAuthProvider.PROVIDER_ID,
      //firebase.auth.PhoneAuthProvider.PROVIDER_ID,
      //firebaseui.auth.AnonymousAuthProvider.PROVIDER_ID

    ],
    // Terms of service url.
    tosUrl: 'https://www.almarcat.com/info/legal-notice/#es',
    privacyPolicyUrl: function () {
      window.location.assign('https://www.almarcat.com/info/legal-notice/#es');
    }
  };

  firebase.auth().setPersistence(firebase.auth.Auth.Persistence.LOCAL)
    .then(function () {
      return firebase.auth().signInWithEmailAndPassword(email, password);
    })
    .catch(function (error) {
      var errorCode = error.code;
      var errorMessage = error.message;
    });

  firebase.auth().onAuthStateChanged(function (user) {
    if (user) {
      // User is signed in, so display the "sign out" button and login info.
      user.getIdToken().then(function (token) {
        // Add the token to the browser's cookies. The server will then be
        // able to verify the token against the API.
        // SECURITY NOTE: As cookies can easily be modified, only put the
        // token (which is verified server-side) in a cookie; do not add other
        // user information.
        document.cookie = "token=" + token + ";expires=" + new Date(new Date().getTime()+60*60*1000*24).toGMTString() + ';path=/';
      });

    } else {
      // User is signed out.
      // Initialize the FirebaseUI Widget using Firebase.
      var ui = new firebaseui.auth.AuthUI(firebase.auth());
      // Show the Firebase login button.
      if (document.getElementById('firebaseui-auth-container')) {
        ui.start('#firebaseui-auth-container', uiConfig);
        // Update the login state indicators.
      }
      //document.getElementById('sign-out').hidden = true;
      //document.getElementById('login-info').hidden = true;
      // Clear the token cookie.
      document.cookie = "token=expired;expires=Sat, 05 Nov 1993 03:00:00 GMT;path=/";
    }
  }, function (error) {
    console.log(error);
    alert('Unable to log in: ' + error)
  });
});