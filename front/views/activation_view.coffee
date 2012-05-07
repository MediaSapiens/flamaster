define [
  'chaplin/view', 'text!templates/activate.hbs'
], (View, template) ->
  'use strict'

  class ActivationView extends View

    autoRender: true
    containerSelector: "#content"
    id: "activate"
    @template = template

    initialize: (options) ->
      if options.hasOwnProperty 'template'
        @template = require(options.template)
      console.log "ActivationView#initialize", options
      super options

    getTemplateData: ->
      data =
        form:
          id: 'activate-form'
          method: 'post'
          action: '.'
      data
