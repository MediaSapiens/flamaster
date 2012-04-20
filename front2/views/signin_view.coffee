define [
  'chaplin/view',
  'text!templates/sign_in.hbs'
], (View, template) ->
  'use strict'

  class SignInView extends View

    autoRender: true
    containerSelector: "#content"
    id: 'signin'
    @template = template

    getTemplateData: ->
      data =
        form:
          id: 'sigin-form'
          method: 'post'
          action: '.'
      data
