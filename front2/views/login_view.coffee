define [
  'chaplin/view',
  'text!templates/login.hbs'
], (View, template) ->
  'use strict'

  class LoginView extends View

    autoRender: true
    containerSelector: '#dialogs'
    id: 'login'
    @template = template

    initialize: (options) ->
      super

      for serviceProviderName, serviceProvider of options.serviceProviders
        console.log "LoginView", serviceProviderName

        buttonSelector = ".#{serviceProviderName}"

        loginHandler = _(@loginWith).bind(
          this, serviceProviderName, serviceProvider
        )

        @delegate 'click'

    loginWith: (serviceProviderName, serviceProvider, e) ->
      e.preventDefault()
      console.debug "LoginView#loginWith",
        serviceProviderName, serviceProvider
