{ProfileModel} = require 'models/profile_model'
{GenericView} = require 'views/generic_view'


class exports.ProfileView extends GenericView
  className: 'profile'
  template: require './templates/profile'

  events:
    "click #profile-form [type='submit']": "saveProfile"

  actions:
    'profile:show': (model) ->
        mediator.trigger 'profile:show', model
    'profile:edit': (model) ->
        mediator.trigger 'profile:edit', model

  initialize: ->
    @model = new ProfileModel

  render: (options) ->
    baseContext = _.extend baseContext,
      profile: options.model

    switch options.action
      when 'profile:edit' then template = require './templates/profile_form'

    @$el.html @template(@baseContext)
    if template?
      @$el.find("#profile-container").html(template(@baseContext))
    @el

  push: (options) ->
    @navigateAnonymous()
    if options.id?
      @model.set id: options.id
      @model.fetch
        success: (model, data) =>
          @actions[options.action](model)
        error: (args...) ->
          console.log 'error', args

  saveProfile: (ev) ->
    data = @serializeForm($(ev.target).parents 'form')
    @model.save data,
      success: (args...) ->
        console.log 'success:', args
      error: (args...) ->
        console.log 'error:', args
    return false
