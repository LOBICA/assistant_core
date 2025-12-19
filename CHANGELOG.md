# CHANGELOG

## NEXT

## v0.9.0
* Update langgraph version to improve security

## v0.8.0
* Replace BaseAgentFactory for ContextFactory for pluggable components (agent/graph/model/tools/resolver)
* Add MultiAgent context and director with conditional entry points
* Add MultiAgentState with `active_agent` selector
* Add an internal-use notice to datetime builder

## v0.7.0
* Update dependencies
* Add validation for new PRs
* Add a builder that adds a prompt with the date and time
* Add option to control entry point on builder
* OpenAI responses API is enabled by default
* Add new load_default_model function
* Deprecated load_openai_model function

## v0.6.4
* Revert back to use "v" prefix for tags

## 0.6.3
* Fix bug with OpenAI API key

## 0.6.2
* Change version tags

## v0.6.1
* Change format of user's answers for question node

## v0.6.0
* Refactor the builder module
* Add builder for Tavily search tool

## v0.5.0
* Updated project documentation
* Add base builder and nodes for assistant workflows

## v0.1.0
* Initial version
