define [
  'chaplin/mediator',
  'chaplin/model'
], (mediator, Model) ->
  'use strict'

  class BaseUser extends Model

    emailRegex: /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/,
    urlRoot: '/account/sessions/'
    defaults:
      email: ''

    initialize: ->
      console.log "User#initialize", @urlRoot

    validate: (attrs) ->
      response = status: 'success'

      unless @emailRegex.test(attrs.email)
        response = status: 'failed', email: 'This is not valid email address'

      return response.status isnt 'success' and response or null

    dispose: ->
      deffered = $.ajax
        url: "/account/sessions/#{encodeURI(@get 'accessToken')}"
        type: 'delete'
        complete: ->
          mediator.router.route '/'
      super
