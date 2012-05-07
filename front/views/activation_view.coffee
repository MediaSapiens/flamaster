define [
  'chaplin/mediator', 'chaplin/view',
  'text!templates/activate.hbs'
], (mediator, View, template) ->
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
      console.log "ActivationView#initialize", mediator.user
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
      console.log "ActivationView#activationHandler", ev
