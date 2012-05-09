define [
  'chaplin/mediator', 'chaplin/view',
  'models/user',
  'text!templates/activate.hbs'
], (mediator, View, User, template) ->
  'use strict'

  class ActivationView extends View

    autoRender: true
    containerSelector: "#content"
    id: "activate"
    @template = template

    initialize: (options) ->
      if options.hasOwnProperty 'template'
        @template = require(options.template)
      # console.debug "ActivationView#initialize", options
      super

      if typeof window.context isnt 'undefined'
        if window.context.hasOwnProperty('user') and window.context.hasOwnProperty('token')
          model_data = _(window.context.user).extend
            token: window.context.token
          @model = new User model_data
          console.debug "ActivationView#initialize", @model
        else
          console.debug "ActivationView#initialize", window.context
      else
        # TODO: need to add template with the wrong token display
        false
      console.debug "ActivationView#model", @model
      @delegate 'submit', "#activate form", @activationHandler

    getTemplateData: ->
      data =
        form:
          id: 'activate-form'
          method: 'post'
          action: '.'
      data

    activationHandler: (ev) ->
      @preventDefault(ev)
      @clearErrors()
      data = @serializeForm ev.target
      console.log "ActivationView#activationHandler", data
      @model.save data,
        success: (model, data) ->
          console.log model
          mediator.publish 'login:pickService', 'custom'
          mediator.publish '!login', 'custom', model.toJSON()
        error: (model, response) => @displayErrors model, response

