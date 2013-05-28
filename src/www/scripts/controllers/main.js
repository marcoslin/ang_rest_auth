'use strict';

// Note that Authenticate is only used here to provide functionality to logout
angular.module('AngRestAuthApp')
    .controller('MainCtrl', function ($scope, $location, Authenticate) {
        $scope.logout = Authenticate.logout;
        $scope.goTo = function (destination) {
            $location.path(destination);
        };

    })
    .controller('ListCtrl', function ($scope, ContactNames) {
        $scope.status = "Ready.";
        $scope.names = ContactNames.query(
            angular.noop,
            function (error) {
                if ( error.data ) {
                    $scope.status = error.data;
                } else {
                    $scope.status = "Failed to get data from server.  Make sure that server is running."
                }
            }
        );
    })
    .controller('DetailCtrl', function ($scope, $routeParams, ContactNames) {
        $scope.status = "Ready.";
        $scope.name = ContactNames.get({ id: $routeParams.id },
            angular.noop,
            function (error) {
                if ( error.data ) {
                    $scope.status = error.data;
                } else {
                    $scope.status = "Failed to get data from server.  Make sure that server is running."
                }
            }
        );
    })
    .controller('HeadersCtrl', function ($scope, HTTPHeaders) {
        $scope.headers = HTTPHeaders.query();
    });
