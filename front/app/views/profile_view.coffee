{ProfileModel} = require 'models/profile_model'

{GenericView} = require 'views/generic_view'

{baseContext, serializeForm} = require 'helpers'

class exports.ProfileView extends GenericView
  className: 'profile'
  template: require './templates/profile'

  actions:
    'profile:show': (id) ->
      (new ProfileModel id: id).fetch
        success: (model, data) -> mediator.trigger 'profile:show', model
        error: (args...) -> console.log args
    'profile:edit': (id) ->
      (new ProfileModel id: id).fetch
        success: (model, data) -> mediator.trigger 'profile:edit', model
        error: (args...) -> console.log args

  render: (options) ->
    console.log 'render', options
    baseContext = _.extend baseContext,
      profile: options.model

    switch options.action
      when 'profile:edit' then template = require './templates/profile_form'

    @$el.html @template(baseContext)
    if template?
      @$el.find("#profile-container").html(template(baseContext))
    @el

  push: (options) ->
    @actions[options.action](options.id)
