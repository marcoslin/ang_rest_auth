'use strict';

angular.module('AngRestAuthApp')
    .controller('LoginCtrl', function ($scope, $location, Authenticate) {
        // If user already logged in, forward to the main page
        if ( Authenticate.get_username() ) {
            $location.path('/main');
        };

        $scope.doLogin = function () {
            Authenticate.login(
                $scope.user_id,
                $scope.password,
                function (error) {
                    $scope.messageStatus = error.data;
                }
            )
        }

        $scope.login_oauth = Authenticate.login_oauth;

    });
