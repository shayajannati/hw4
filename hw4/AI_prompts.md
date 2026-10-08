# AI Prompts — Homework 4

Running log of the prompts used for each problem. Each section records the prompt as
given and, where a follow-up was needed, the follow-up prompt plus one sentence on what
the first attempt was missing.

## Problem 1: Vibe coder prompts

> We are starting Homework 4. Before we begin the coding problems, please create a file called AI_prompts.md in the root of my homework folder. This file will be a running log of the prompts I give you throughout the assignment.
> Organize it with a section for each homework problem as we complete them. Each section should include the problem number and title, the prompt I gave you, and, if I needed a follow-up prompt, the follow-up prompt plus one sentence explaining what was missing after the first attempt.
> Start the file with a section called Problem 1: Vibe coder prompts and record this prompt there. Do not invent any future prompts or fill in future problems yet. We will add them as we work.

## Problem 2: Analyze the database

> Now let's do Problem 2: Analyze the database.
> Please inspect data/campus_customs.db and determine the actual structure of the database rather than guessing. At minimum, inspect the catalogue, inventory, and users tables, but also tell me if there are any other tables.
> For each table, identify all of its fields/columns and briefly explain in plain English what each field is used for and why it matters for the Campus Customs shop or chatbot. Please also look at a small sample of the data when helpful so you understand what the fields represent, but do not modify the database.
> Create output/harness.md and document the database structure there. We will continue adding to this same harness file in later problems, so do not add information about features we have not built yet.
> Also update AI_prompts.md with a new section titled Problem 2: Analyze the database and record this prompt exactly as I gave it to you.
> When you are finished, summarize what you discovered about the database in plain English so I can understand it before we move on.

## Problem 3: Build the storefront

> Let's do Problem 3: Build the storefront.
> Build the frontend for the Campus Customs online store using React, Vite, and TypeScript. Use the actual Campus Customs product data from data/campus_customs.db and the corresponding product images in data/products/. Do not invent products, prices, images, or inventory information.
> Create a polished storefront that displays the products in a browsable product grid. Each product card should show the appropriate product image, product name, and price. Make the layout clean, responsive, and appropriate for an online college apparel store.
> When a user clicks a product card, show a single-item product view with that product's information. Build the product card and single-item product view as reusable components because later the chatbot will need to return clickable product results that use the same product-view behavior.
> Preserve the product IDs from the database so products can be reliably connected to inventory and chatbot results in later problems.
> Please set up the frontend using the normal React + Vite + TypeScript project structure and make sure it can be run locally. Do not build the chatbot, authentication system, or later homework features yet.
> After implementing it, test that the frontend starts successfully and that the product grid and single-item product view work. Tell me what files you created or changed, how the storefront gets its product information, and the exact command I should use to run it locally.
> Update AI_prompts.md with a section titled Problem 3: Build the storefront and record this prompt exactly as I gave it to you.

## Problem 4: Add user accounts

> Let's do Problem 4: Add user accounts.
> Add user authentication to the Campus Customs storefront. Use the existing `users` table in `data/campus_customs.db` rather than creating a separate user system.
> Users should be able to create a new account, log in with their email and password, stay logged in while using the storefront, and log out. Integrate the authentication interface cleanly into the existing React storefront without breaking the product grid, search, product cards, or single-item product pages from Problem 3.
> Passwords must never be stored in plain text. New account passwords should be securely salted and hashed in a format compatible with the existing database authentication system. Do not expose password hashes or other sensitive user information to the frontend or logs.
> Inspect the existing `users` table and existing password-hash format before implementing authentication so you do not guess how the seeded accounts work.
> Test authentication in two ways:
>
> 1. Verify that an existing seeded user from the database can successfully log in using the appropriate provided/test credentials available in the homework data or project materials. Do not change that seeded user's password just to make the test pass.
> 2. Create a new test account through the application, verify that it can log in and log out successfully, and confirm that its password is stored as a secure salted hash rather than plain text.
>
> Keep all changes within the `hw4` project. Do not modify my `hw3` folder or unrelated files.
> When you finish, explain in plain English how signup, login, logout, password hashing, and the logged-in state work. Tell me which files you created or changed and exactly how I can test the feature myself.
> Finally, update `AI_prompts.md` with a section titled `Problem 4: Add user accounts` and record this prompt exactly as I gave it to you.

## Problem 5: Build the chatbot backend

> Let's do Problem 5: Build the chatbot backend.
> Build the initial AI chatbot backend for the Campus Customs storefront using FastAPI and PydanticAI. Integrate it into the existing backend without breaking the authentication functionality from Problem 4.
> Use the exact backend structure required for this assignment. Create or update the appropriate backend files, including:
>
> * `backend/main.py`
> * `backend/models.py`
> * `backend/agent.py`
> * `backend/tools.py`
> * `backend/prompts/prompt.md`
>
> The chatbot should use PydanticAI for the agent rather than implementing a custom model-calling loop. Load the chatbot's system prompt from `backend/prompts/prompt.md` rather than hard-coding the full prompt inside the Python code.
> Create the FastAPI chat endpoint required for the frontend to send a customer message and receive the agent's response. Use clear Pydantic request and response models in `backend/models.py`.
> For this problem, focus on establishing the chatbot backend and basic agent behavior. Do not invent product prices, inventory quantities, or product availability. Those must eventually come from the database through tools rather than the language model's memory. Do not implement later homework features unless they are necessary for this problem.
> Make the system prompt appropriate for a Campus Customs shopping assistant. It should clearly establish the assistant's role and prevent it from claiming unsupported product, price, or inventory information.
> Keep API keys and other secrets out of the source code. Use environment variables as appropriate and make sure the real `.env` is excluded from git. Do not expose secrets in logs, output files, or `AI_prompts.md`.
> Keep all changes inside the `hw4` project and do not modify `hw3` or unrelated files.
> Update `requirements.txt` with the Python dependencies needed for the chatbot backend.
> Test that the backend starts successfully and that the chat endpoint can accept a message and return a valid response through the PydanticAI agent. Do not claim a live-model test succeeded if the required API credentials are unavailable; distinguish clearly between tests that actually ran and tests that could not run.
> Update `output/harness.md` with the relevant Problem 5 information about the agent architecture, model setup, system prompt, and how the chatbot backend runs. We will continue expanding this file in later problems.
> Finally, update `AI_prompts.md` with a section titled `Problem 5: Build the chatbot backend` and record this prompt exactly as I gave it to you.
> When finished, explain in plain English how a customer's message travels from the API endpoint to the PydanticAI agent and back, which AI model is being used and where that model is configured, which files you created or changed, what you actually tested, and the exact command I should use to run the backend.

> Before we move to Problem 6, I want to correct one missing requirement from Problem 5. The Problem 5 chatbot needs to be plugged into the frontend chat widget, so please add the frontend chat interface now and connect it to the /api/chat endpoint you already built.
> Add a clean, usable chat widget to the existing Campus Customs React storefront without breaking the product grid, search, individual product pages, or authentication.
> A customer should be able to open the chat widget, type a message, send it, and see both their message and the chatbot's response in the conversation. The frontend should send the conversation to the existing FastAPI/PydanticAI backend and display the returned response. If the backend returns product information that can already be represented using the existing reusable product components, preserve that data for later use, but do not jump ahead and implement the dynamic clickable search-result cards required in a later problem.
> Include appropriate loading and error states so the interface does not appear frozen while waiting for the model and gives the user a useful message if the backend is unavailable.
> Keep the existing Portkey + gpt-5.6-luna + PydanticAI backend architecture unchanged unless a small integration change is necessary. Keep all changes inside hw4.
> Test the frontend-to-backend chat flow if possible. Verify that sending a message from the frontend reaches /api/chat and that the response can be rendered by the chat widget.
> Because this is a follow-up for Problem 5, append this exact follow-up prompt under Problem 5: Build the chatbot backend in AI_prompts.md, followed by one sentence explaining that the first attempt built and tested the chatbot backend but did not add the required frontend chat widget.
> Tell me what you changed and what you actually tested.

The first attempt built and tested the chatbot backend but did not add the required frontend chat widget.

## Problem 6: Database tools

> Let's do Problem 6: Database tools.
> Expand the Campus Customs PydanticAI agent so it can answer factual customer questions about products, prices, and inventory using the real data in `data/campus_customs.db`.
> Implement the required database-backed tools in `backend/tools.py`. The tools should allow the agent to:
>
> * search for products using the catalogue;
> * retrieve the authoritative price for a specific product from the database;
> * check inventory for a specific product and size and return the actual quantity in stock.
>
> Use the real `catalogue` and `inventory` tables and their actual schema that we inspected in Problem 2. Do not hard-code product names, prices, stock quantities, or availability.
> Make the tools read-only. The chatbot should not be able to change catalogue or inventory data.
> Wire every tool into the PydanticAI agent in `backend/agent.py` so the model can actually call them. Do not merely define unused functions in `tools.py`.
> Update `backend/prompts/prompt.md` so the shopping assistant understands when to use the database tools. Make it explicit that product prices and inventory/size availability must come from the tools and must never be guessed or inferred by the language model. If a product cannot be identified reliably or the database does not provide the requested information, the assistant should say that rather than inventing an answer.
> Update `backend/models.py` as needed so tool results and agent responses have clear structured types.
> Preserve everything that already works from Problems 3–5, including the storefront, authentication, chat widget, Portkey integration, `gpt-5.6-luna`, conversation history passed by the widget, and the existing product search functionality.
> Test the tools directly against the database and also test them through the actual PydanticAI agent. Include tests for:
>
> * finding a real product;
> * retrieving that product's exact database price;
> * checking a real size with stock available;
> * checking a real size with zero stock;
> * an invalid product;
> * an invalid size;
> * a natural-language customer question that requires the agent to call the database tools for price and inventory.
>
> Verify that the values returned through the chatbot match the database exactly. Also verify that the tools cannot modify the database.
> Keep all changes inside `hw4`.
> Update `output/harness.md` with the Problem 6 database tools, what each tool does, what data it accesses, and the fact that the tools are read-only. Continue using the existing harness rather than replacing it.
> Update `AI_prompts.md` with a section titled `Problem 6: Database tools` and record this prompt exactly as I gave it to you.
> When you're finished, explain in plain English what tools the agent now has, show me an example of how a price or inventory question travels from the customer to the agent to the database and back, tell me what files you changed, and report the tests you actually ran and their results.

## Problem 7: Dynamic product cards

> Let's do Problem 7: Dynamic product cards.
> Update the Campus Customs chat experience so product matches returned by the chatbot are dynamically rendered as clickable product cards in the chat.
> Use the structured product results already returned by /api/chat. Do not hard-code particular products or map specific customer phrases to specific cards in the frontend.
> When a chatbot response contains product matches, render those products underneath the appropriate assistant message using the existing reusable product-card/product-view architecture from Problem 3. Each chat result should show the correct product image, product name, and authoritative database price.
> Clicking a product returned by the chatbot must open the same single-item product view used when a customer clicks a product from the main storefront. Preserve the existing #/product/<product_id> behavior rather than creating a separate chatbot product page.
> Make sure the cards correspond specifically to the products returned for that assistant response. A later message should not overwrite or incorrectly attach its products to an earlier message.
> The cards must be dynamic: different customer searches should result in different cards based on the agent/database results. Do not hard-code search-result products in React.
> Preserve all existing functionality, including the main storefront product grid, storefront search, single-item product pages, authentication, chat conversation display, loading/error states, PydanticAI agent, Portkey with gpt-5.6-luna, and the Problem 6 database tools.
> Test at least two meaningfully different natural-language product searches through the actual chat flow and verify that they produce the correct different product cards. Also verify that clicking a chatbot product card uses the existing single-item product view and that clicking a regular storefront product still works as before.
> Verify that the displayed product name, image, price, and product ID correspond to the real product data and that no product cards are fabricated by the language model or hard-coded in the frontend.
> Keep all changes inside hw4.
> Update output/harness.md with the relevant Problem 7 behavior, including how structured product matches travel from the agent/backend to the frontend and become product cards.
> Update AI_prompts.md with a section titled Problem 7: Dynamic product cards and record this prompt exactly as I gave it to you.
> When finished, explain in plain English how the product cards are generated dynamically, how clicking one connects to the existing single-item view, which files you changed, and exactly what you tested.

## Problem 8: Customer context and persistent chat history

> Let's do Problem 8: Customer context and persistent chat history.
> Extend the Campus Customs chatbot so it understands the logged-in customer's identity, preserves chat history for logged-in users, and understands the customer's current storefront/product context.
> Use the existing authentication system and the existing `chat_messages` table in `data/campus_customs.db`. Do not create a separate database or duplicate user/chat-history system.
> For logged-in users, load their saved chat history from `chat_messages` when the storefront/chat initializes. When they send a new message and receive an assistant response, persist both messages to `chat_messages` under the correct authenticated user. Preserve any structured product references in the format expected by the existing database schema so product cards can be reconstructed when saved conversations are loaded again.
> Keep different users' histories completely separate. A logged-in user must never receive another user's chat history.
> Guests who are not logged in should still be able to use the chatbot normally during their current visit, but their messages should not be written to persistent account history in `chat_messages`.
> Give the agent useful customer identity context for authenticated users, such as the customer's name, without exposing sensitive information such as password hashes or authentication secrets.
> Also pass the customer's current storefront context to the chatbot. In particular, when the customer is viewing a single product at `#/product/<product_id>`, provide that validated product ID to the backend/agent so questions such as "How much is this?", "Do you have this in medium?", or "Tell me more about this" can refer to the product currently being viewed.
> Do not trust an arbitrary product ID from the browser. Validate the current product ID against the catalogue before using it as agent context. The model should continue using the Problem 6 database tools for authoritative price, description, and inventory information rather than treating frontend context as proof of those facts.
> Preserve all existing behavior from Problems 3–7, including authentication, the storefront, product search, individual product views, the chat widget, dynamic product cards, PydanticAI, Portkey with `gpt-5.6-luna`, and all database tools.
> Test at least the following:
>
> * a logged-in user's new customer and assistant messages are saved to `chat_messages`;
> * refreshing/reloading the application restores that user's previous chat history;
> * saved product references restore the appropriate product cards;
> * two different users receive only their own histories;
> * a guest can chat but does not create persistent `chat_messages` rows;
> * while viewing a real product page, a question such as "How much is this?" resolves to that product and gets its authoritative database price;
> * while viewing a product page, a size/stock question about "this" uses the inventory tool for that product;
> * an invalid product ID supplied as page context is rejected or ignored rather than trusted;
> * authentication, normal product searches, and dynamic product cards still work.
>
> Be careful with the existing rows already present in `chat_messages`. Do not treat seeded historical rows as though this implementation created them, and do not overwrite or delete another user's existing conversation history merely to make testing easier.
> Keep all changes inside `hw4`.
> Update `backend/models.py`, `backend/main.py`, `backend/agent.py`, the frontend chat code, and any other existing files as necessary. Continue using the existing database schema where possible rather than redesigning unrelated parts of the project.
> Update `output/harness.md` with the Problem 8 behavior, including how authenticated identity is established, how chat messages are persisted and retrieved, how guest behavior differs, how current-page/product context reaches the agent, and how user histories remain isolated.
> Update `AI_prompts.md` with a section titled `Problem 8: Customer context and persistent chat history` and record this prompt exactly as I gave it to you.
> When finished, explain in plain English how identity, saved history, guest chat, and current-product context work; tell me which files changed; and report the tests you actually ran and their results.

## Problem 9: Usability improvements

> Let's do Problem 9: Usability improvements.
> Implement exactly four usability improvements to the Campus Customs application: exactly 2 frontend improvements and exactly 2 agent/backend improvements. Do not count or describe more than these four as Problem 9 improvements.
> Before changing anything, briefly inspect the existing application and confirm that each proposed improvement is genuinely new and was not already implemented in Problems 3–8.
> Implement these four improvements:
> Frontend Improvement 1: Chat reset/new conversation control
> Add a clear "New chat" or "Clear chat" control to the chat widget.
> For a guest, this should clear the current in-memory conversation.
> For a logged-in user, do not silently delete their persistent database history. The control should start a fresh visible conversation/session without destroying previously stored database records unless the assignment explicitly requires deletion. Make the behavior clear to the customer.
> Frontend Improvement 2: Better empty and no-results states
> Improve the storefront/search experience so customers receive a clear, useful message when a product search returns no results rather than seeing an unexplained empty area. Give them an easy way to clear/reset the search and return to the full catalogue.
> Agent/Backend Improvement 1: Helpful product-search fallback
> When a customer's product search produces no exact/relevant matches, make the chatbot respond helpfully rather than inventing products or ending with an unhelpful failure. It should clearly say that it could not find a matching product and, where appropriate, suggest a broader search or ask the customer to clarify what they want.
> Keep all product facts grounded in the database. Do not fabricate alternatives.
> Agent/Backend Improvement 2: Better handling of ambiguous product references
> Improve the agent's handling of ambiguous requests where multiple products could match what the customer means. Instead of arbitrarily choosing one product for a price, description, or inventory lookup, have it ask the customer to clarify which matching product they mean or present the relevant real options so the customer can choose.
> This should work naturally with conversation history so the customer's clarification can be understood in the next message.
> These are the only four improvements that should be identified and counted as Problem 9 usability improvements. Preserve all existing behavior from Problems 3–8.
> Test each of the four improvements through the appropriate real application path. For the two agent/backend improvements, use the actual PydanticAI agent and database-backed tools rather than mocking the answer. Also regression-test authentication, persistent history, current-product context, dynamic product cards, and normal product search.
> Create `output/usability.md`. Clearly document exactly four sections:
>
> 1. Frontend Improvement 1
> 2. Frontend Improvement 2
> 3. Agent/Backend Improvement 1
> 4. Agent/Backend Improvement 2
>
> For each one, explain the usability problem, what you changed, why it improves the customer experience, and how you tested it.
> Do not list existing functionality from Problems 3–8 as additional Problem 9 improvements.
> Update `output/harness.md` only as needed to accurately reflect the resulting application.
> Update `AI_prompts.md` with a section titled `Problem 9: Usability improvements` and record this prompt exactly as I gave it to you.
> Keep all changes inside `hw4`.
> When finished, report exactly the four improvements, the files changed, the tests you actually ran and their results, and confirm that `output/usability.md` contains exactly two frontend and two agent/backend improvements.

## Problem 10: Creative storefront styling

> Let's do Problem 10: Creative storefront styling and design.
> I want the Campus Customs storefront to have a distinctive Yale-inspired visual identity while preserving all functionality from Problems 3–9.
> Please redesign the frontend around this creative direction:
> Overall aesthetic: classic Yale collegiate style, polished but cute and playful rather than overly corporate.
> Yale-inspired colors: use a Yale-blue-centered palette with complementary white, cream, and other subtle neutral tones. Keep text readable and maintain good contrast.
> Typography: use attractive collegiate/editorial-style fonts. I want the typography to feel cute and distinctive while still being easy to read. Avoid adding font files that we do not have permission to redistribute. Prefer safe web/system fonts or appropriately licensed dependencies/assets.
> Handsome Dan mascot: incorporate a tasteful bulldog/Handsome Dan-inspired mascot element into the storefront. I would especially like a cute bulldog wearing a Yale-style sweater if that can be created using an original or legally usable asset. Do not scrape or copy a copyrighted mascot image from a random website. Keep the mascot decorative and make sure it does not interfere with shopping or chat functionality.
> Campus-inspired side borders: create decorative borders or margins along the sides of the website inspired by Yale's campus and architecture. I would like these to feel like a visual collage/frame of Yale campus imagery if suitable reusable assets are available. If we do not already have legally usable Yale campus photos in the project, do not download random copyrighted photographs just to satisfy this idea. Instead, create an original campus-inspired treatment using architectural silhouettes, line-art-style elements, decorative collegiate motifs, or other locally created assets. The center shopping area should remain clean and readable.
> Paw-print cursor trail: add a playful mouse effect where moving the cursor leaves a short, temporary trail of small bulldog paw prints that fades away. Keep it subtle so it does not make the website difficult to use. It should not block clicks, should disappear quickly, and should respect prefers-reduced-motion so users who request reduced motion do not get the animated trail.
> Make the overall page feel intentionally designed as one coherent Campus Customs/Yale storefront rather than adding disconnected decorations.
> Preserve all functionality from Problems 3–9. Do not break the 102-product storefront, search, no-results state, individual product pages, authentication, persistent chat history, New Chat behavior, current-product context, PydanticAI chatbot, database tools, or dynamic clickable product cards.
> Keep the responsive layout usable on narrower screens. Decorative side borders may simplify or disappear when there is not enough screen width.
> Do not change factual product information or hard-code product results for the sake of the design.
> Test the redesigned application for regressions and verify that decorative elements do not block buttons, links, product cards, search, authentication, or the chat widget. Verify the paw trail does not capture pointer events and that reduced-motion behavior works.
> Create output/design.md describing the design direction and the creative choices actually implemented. Explain the color palette, typography, mascot treatment, campus-inspired borders, paw-print cursor trail, responsive/accessibility considerations, and why these choices fit the Campus Customs storefront.
> Update output/harness.md only where needed to reflect the final application.
> Update AI_prompts.md with a section titled Problem 10: Creative storefront styling and record this prompt exactly as I gave it to you.
> Keep all changes inside hw4.
> When finished, tell me exactly what visual changes you implemented, what assets you created or used and where they came from, which files changed, and what tests you actually ran.

> wait what animal is that it does not look like a bulldog. its cute tho. maybe just fix the ears

> the mouth ears are still a little wonky. i dont think it needs teeth or a literal smile. try to make it more similar to this

The first mascot didn't read clearly as a bulldog (ears and mouth looked off), so these follow-ups redrew the ears and then the face in a chunkier cartoon-bulldog style based on a reference image.

> the mouth is really bad. the lines on the face are convex not concave. also the tongue looks like a fully mouth and isnt attached

The redrawn mouth still curved the wrong way and its tongue sat inside a separate mouth shape, so this follow-up changed it to a concave dog smile with the tongue hanging from the mouth line.

> this is better but the tongue lines extend too far above the face flaps and there is a gap at the top. i also want the face flaps to be bigger. does this image help as inspiration can you use it?

The tongue's outline still poked above the mouth with a gap, and the jowl flaps were too small, so this follow-up enlarged the flaps and clipped the tongue to hang directly from the smile line.

> i like the tongue and mouth but everything else can still use a bit more work. the jowls should connect above the nose like this. also the ears now look like a bear. use this as jowl and ear inspiration

The jowls were two separate flaps and the ears looked like a bear's, so this follow-up made the muzzle one shape arching over the nose and redrew the ears as floppy folded flaps.

> why did you make it angry? get rid of the lines above the eyes and draw the eyes like this

> also make the nose mushroom shaped like that

The forehead wrinkle lines between the eyes made the mascot look angry and the eyes and nose didn't match the reference style, so these follow-ups removed the lines, redrew the eyes as big friendly eyes with highlights, and made the nose mushroom-shaped.

> the nose needs to be a bit smaller and the eyes should be lower and right above the line connecting the jowls

The nose was too large and the eyes sat too high above the muzzle line, so this follow-up shrank the nose and moved the eyes down onto the muzzle line.

> reduce the space between the eyes a bit one last time

The eyes were set slightly too far apart, so this final follow-up moved them closer together.

## Problem 11: Application testing

> Let's do Problem 11: Application testing and screenshot evidence.
> Test the final Campus Customs application as a real user in an actual browser. This problem requires browser-based evidence, so do not substitute Node, jsdom, API-only tests, component rendering tests, or written claims for the required browser testing and screenshots.
> First, reread the exact Problem 11 assignment requirements available in this homework and make a checklist of every required test/evidence item before testing. Follow the literal filenames, paths, screenshot requirements, and output format from the assignment.
> At minimum, the browser testing and screenshot evidence must visibly demonstrate:
>
> 1. Inventory lookup: use the chatbot to ask a real inventory/size question that requires the Problem 6 inventory tool. The resulting browser state should visibly show the product and actual inventory answer.
> 2. Dynamic product search cards: ask the chatbot for a product category/search and capture the browser showing dynamically returned clickable product cards. Use a search that produces a clear set of real products from the database.
> 3. At least one Problem 9 usability improvement: visibly demonstrate one of the implemented Problem 9 features in the browser. Prefer a feature that is easy for a grader to recognize from a screenshot, such as the improved no-results state with its Clear Search control or the New Chat behavior.
>
> Save the required screenshots inside:
> `output/app_check_images/`
> Create:
> `output/app_check.html`
> The HTML report must document the application checks and display/link the screenshot evidence using relative paths to `app_check_images`, so the report continues to work when the homework is moved to another computer or uploaded to GitHub. Do not use absolute paths such as `/Users/...`.
> For every screenshot/evidence item, clearly state what was tested, what action was taken, what result was expected, what actually happened, and why the screenshot proves the requirement.
> Use the actual final application after Problem 10, including the Yale styling. Make sure the screenshots show the real running storefront rather than isolated components or test-rendered HTML.
> For the inventory screenshot, verify the quantity shown in the chatbot against `data/campus_customs.db` so we know the displayed value is correct. Do not alter the database to manufacture a convenient result.
> For the dynamic-product-card screenshot, verify that the cards shown correspond to the actual products returned from the database and that clicking at least one of those cards opens the existing single-item product view.
> For the Problem 9 feature, test the feature itself rather than merely showing that its button exists.
> Also perform reasonable regression checks on the final application, including storefront loading, all 102 products, search, individual product pages, authentication, chatbot, persistent history for a logged-in user, guest behavior, current-product context, dynamic cards, Problem 9 improvements, and the Problem 10 responsive/decorative behavior. Follow any additional checks explicitly required by the Problem 11 assignment.
> Be careful with test data. Do not modify the original 22 seeded `chat_messages` rows. Use our own test account or guest mode where appropriate. If testing creates new rows for our test accounts, report exactly what was added rather than silently changing seeded data.
> Do not modify application behavior merely to make screenshots easier to obtain. If a test fails, diagnose and fix the underlying application, rerun the relevant test, and document the final passing state.
> After creating the report, verify that every screenshot file referenced by `output/app_check.html` actually exists in `output/app_check_images/` and that every `<img>` or link uses a valid relative path. Open the final HTML report and verify that the images actually render.
> Update `AI_prompts.md` with a section titled `Problem 11: Application testing` and record this prompt exactly as I gave it to you.
> Update `output/harness.md` only if the Problem 11 assignment requires information that is not already documented.
> Keep everything inside `hw4`.
> When finished, report:
>
> * the exact Problem 11 requirements you found in the assignment;
> * every browser test you actually performed and its result;
> * the exact screenshot filenames created;
> * what each screenshot proves;
> * confirmation that `output/app_check.html` uses working relative paths and displays the screenshots;
> * any bugs discovered and fixed during testing;
> * any database rows added during testing;
> * the files changed.
>
> Do not call Problem 11 complete if any required screenshot or evidence item could not actually be produced.

> Test the final Campus Customs application in an actual browser and create the required testing evidence.
> For this problem, the required evidence is:
>
> * browser evidence of a successful inventory lookup;
> * browser evidence of dynamic product search cards returned by the chatbot;
> * browser evidence of one Problem 9 usability improvement;
> * screenshots saved in `output/app_check_images/`;
> * an `output/app_check.html` report that documents the testing and references the screenshots using relative paths.
>
> Do not substitute Node, jsdom, API-only tests, component rendering, or written claims for the required browser screenshots. The screenshots must show the actual final Campus Customs application running in a browser.
> Test 1 — Inventory lookup
> In the actual chatbot, ask a real inventory/size question that requires the Problem 6 inventory tool. Capture a screenshot showing the chatbot's inventory answer in the running application. Independently verify that the quantity shown matches `data/campus_customs.db`.
> Test 2 — Dynamic product cards
> In the actual chatbot, make a natural-language product search that returns multiple real products. Capture a screenshot showing the resulting dynamic clickable product cards in the chat. Verify the displayed products against the database. Click at least one returned card and verify that it opens the existing single-item product view from Problem 3.
> Test 3 — Problem 9 usability feature
> Demonstrate one of the Problem 9 usability improvements in the actual browser and capture screenshot evidence of the feature working. Use the improved storefront no-results state and Clear Search control because it is visually easy to verify: enter a search that genuinely returns no products, show the resulting no-results state, and verify that using Clear Search restores the catalogue.
> Save all screenshot files under:
> `output/app_check_images/`
> Create:
> `output/app_check.html`
> The HTML report must include the testing evidence and reference the screenshots with relative paths such as:
> `app_check_images/example.png`
> Do not use absolute `/Users/...` paths.
> For each required test in `output/app_check.html`, document what was tested, the action taken, the expected result, the actual result, and which screenshot proves it.
> Verify that every screenshot referenced by `output/app_check.html` actually exists and that the images render when the HTML file is opened.
> Use the final Problem 10 version of the application so the screenshots show the finished Yale-styled storefront.
> Also regression-test the major existing functionality without treating those regression checks as substitutes for the three required screenshot tests: the 102-product storefront, normal search, individual product pages, authentication, chatbot, logged-in persistent history, guest chat behavior, current-product context, dynamic product cards, and the Problem 9 improvements.
> Do not modify or delete the original 22 seeded `chat_messages` rows. Use our own test account or guest mode as appropriate. Report any test rows that are added.
> If browser testing exposes a real application bug, fix the underlying problem and rerun the affected test. Do not modify the application merely to manufacture screenshot evidence.
> Update `AI_prompts.md` with a section titled `Problem 11: Application testing` and record this prompt exactly as I gave it to you.
> Keep all work inside `hw4`.
> When finished, report:
>
> * every actual browser test performed and whether it passed;
> * the exact screenshot filenames created;
> * what each screenshot proves;
> * confirmation that the screenshots are in `output/app_check_images/`;
> * confirmation that `output/app_check.html` uses working relative paths and actually displays them;
> * any bugs found and fixed;
> * any database rows created during testing;
> * every file changed.
>
> Do not call Problem 11 complete unless all three required categories have actual browser screenshot evidence.

The first prompt left the Problem 9 demonstration open; this restated prompt (sent while testing was running) fixed Test 3 as the no-results state with Clear Search and restated the evidence and reporting requirements.

## Problem 12: Audit trail, safety, and final harness

> Let's do Problem 12: Audit trail, safety, and final harness.
> Complete the audit, safety, and documentation requirements for the Campus Customs AI application while preserving all functionality from Problems 3–11.
> 1. Create an append-only audit trail
> Create:
> `output/audit_trail.json`
> The application must record agent activity to this audit trail in an append-only manner. Existing audit records must never be silently overwritten, rewritten, or deleted when a new event is recorded.
> Use valid JSON in the format required by the application/assignment. If maintaining a single JSON array would require rewriting the entire file for every event, implement the safest approach that still satisfies the required `output/audit_trail.json` filename and append-only requirement. Do not invent a different filename merely for convenience.
> Record enough structured information to make important chatbot activity auditable, including appropriate information about requests, responses, tool use, results/outcomes, timestamps, and errors where relevant.
> Do not put secrets or sensitive authentication information in the audit trail. Never log API keys, Portkey credentials, password hashes, session-cookie secrets, raw authentication cookies, or other credentials.
> 2. Add and document explicit safety rules
> Make the agent's safety behavior explicit in the appropriate system prompt/code. At minimum:
>
> * product prices must come from the authoritative database tools and must never be guessed;
> * inventory and size availability must come from the authoritative database tools and must never be guessed;
> * the agent must not invent products;
> * ambiguous product references should be clarified rather than arbitrarily selecting a product;
> * unknown products or unavailable information should be handled honestly;
> * database access used by agent tools must remain read-only;
> * customer identity must come from the authenticated backend/session rather than a user-supplied user ID;
> * one customer's saved history must never be exposed to another customer;
> * sensitive values such as password hashes, session secrets, API keys and Portkey credentials must never be returned to customers or written to the audit trail;
> * current-product context from the frontend must be validated against the catalogue before the agent relies on it.
>
> Preserve any existing safety behavior that is stricter than these rules.
> 3. Add explicit agent execution limits
> Configure and document appropriate limits for the PydanticAI agent so an individual customer request cannot cause an uncontrolled or infinite agent/tool loop.
> Include appropriate limits on model requests/tool-loop behavior and on the number/size of results returned by tools where relevant.
> Use the actual supported PydanticAI mechanisms for the installed version rather than merely describing limits in documentation. Do not replace PydanticAI with a hand-written agent loop.
> Inspect the installed PydanticAI version/API before choosing the exact limit configuration so the implementation uses valid framework-supported settings.
> 4. Complete `output/harness.md`
> Treat `output/harness.md` as the final technical description of the finished application.
> It must accurately document at least:
>
> * the model or models actually used by the application;
> * PydanticAI as the agent framework;
> * Portkey/model-provider configuration;
> * every agent tool, what it does, what database information it accesses, and the important structured result/model fields;
> * why those result/model fields were chosen where required by the earlier database-tool work;
> * the fact that database-backed agent tools are read-only;
> * the system/safety rules governing the agent;
> * the agent loop/model-request limits;
> * tool result limits or other relevant result-size limits;
> * authenticated customer identity and history isolation;
> * current-product context and its validation;
> * persistent chat-history behavior for logged-in users and guest behavior;
> * the audit trail, what events it records, and what sensitive information it deliberately excludes;
> * the exact commands needed to install dependencies and run the backend and frontend from a fresh local checkout;
> * required environment variables and how `.env.example` is used, without putting any real secret values in the harness;
> * any important ports/directories required by the run commands.
>
> Make sure the run instructions match the actual final code, filenames, directories, dependencies, and ports. Do not document hypothetical commands that were not verified.
> 5. Verify the implementation
> Test the audit trail through the real PydanticAI application. Generate representative activity that includes:
>
> * a normal product search;
> * a product-details/price lookup;
> * an inventory lookup;
> * an ambiguous-product interaction;
> * a no-match/unknown-product interaction;
> * at least one handled error or safe rejection if one can be tested without deliberately damaging the application.
>
> Verify that the corresponding audit records are added and that previous records remain intact.
> Verify that the audit trail contains no API keys, password hashes, session secrets, raw cookies, or other credentials.
> Test the configured agent execution limits and confirm they are actually enforced by the application/framework rather than existing only in `harness.md`.
> Verify the database-backed agent tools still cannot write to `data/campus_customs.db`.
> Regression-test the important existing functionality, including authentication, persistent history, guest chat, current-product context, product search, authoritative price/inventory answers, ambiguity handling, dynamic product cards, and the storefront.
> Do not alter the original seeded application data merely to make a test pass.
> 6. Prompt log
> Update `AI_prompts.md` with a section titled:
> `Problem 12: Audit trail, safety, and final harness`
> Record this prompt exactly as I gave it to you. If you need a follow-up prompt from me to satisfy a missing requirement, log that follow-up and explain in one sentence what the first attempt lacked, consistent with the existing prompt-log format.
> Keep all work inside `hw4`.
> When finished, report:
>
> * the exact audit-trail format you implemented and why it satisfies append-only behavior;
> * several representative audit records/events that were generated, without exposing secrets;
> * where the audit logging happens in the code;
> * the safety rules that are actually enforced and where;
> * the exact PydanticAI execution/loop limits implemented and where;
> * any tool/result limits;
> * the final model and agent configuration;
> * the sections now present in `output/harness.md`;
> * the exact verified install/run commands documented in the harness;
> * every test you actually ran and its result;
> * the files changed.
>
> Do not call Problem 12 complete if a safety rule, execution limit, audit requirement, or required harness item exists only in documentation but is not actually implemented where implementation is required.

## Problem 13: Final GitHub submission

> Let's do Problem 13: Final GitHub submission.
> Prepare the completed Campus Customs Homework 4 project for submission as a public GitHub repository.
> The final submission is the public GitHub repository URL, not a ZIP file.
> Before creating or pushing anything, perform a strict final audit of the project and repository contents. Do not expose any secrets or private data.
> 1. Required repository contents
> Make sure the public repository contains the source code and documentation necessary to understand and run the project, including:
>
> * frontend source code;
> * backend source code;
> * `AI_prompts.md`;
> * `README.md`;
> * `requirements.txt`;
> * `.env.example`;
> * `.gitignore`;
> * the required `output/` deliverables from the homework, including the final `output/harness.md`, `output/usability.md`, `output/design.md`, `output/app_check.html`, `output/app_check_images/`, and `output/audit_trail.json`;
> * any original decorative assets needed by the frontend, including the Problem 10 Yale-inspired assets;
> * package/dependency files needed to install and run the frontend.
>
> Preserve other legitimate source/configuration files that the application requires to run.
> 2. Files that must NOT be committed
> The public GitHub repository must NOT contain:
>
> * `data/campus_customs.db`;
> * the supplied product image files from `data/products/`;
> * a real `.env` file;
> * API keys;
> * Portkey credentials;
> * session secrets;
> * authentication cookies;
> * password hashes or exported user credentials;
> * virtual environments such as `.venv/`;
> * `node_modules/`;
> * local caches;
> * temporary test artifacts;
> * OS/editor junk;
> * other secrets or private local configuration.
>
> Make sure `.gitignore` explicitly protects the database, product-image directory, `.env`, `.venv`, `node_modules`, and other generated/private files as appropriate.
> Do not assume `.gitignore` is enough. Before publishing, inspect the actual Git staging/tracked-file list and verify that prohibited files are not already tracked.
> 3. Secret/privacy audit
> Search the files that would actually be committed for accidental secrets or sensitive information.
> Check for things such as:
>
> * API keys and tokens;
> * Portkey credentials;
> * session secrets;
> * `.env` values;
> * raw cookies;
> * password hashes;
> * accidentally hard-coded credentials;
> * sensitive values in logs, audit files, screenshots, HTML reports, documentation, or prompt logs.
>
> Do not print real secrets into your response while checking them. Report only whether something unsafe was found and where it was remediated.
> Also inspect the Problem 11 screenshots and HTML report for accidentally visible sensitive information before publishing them.
> 4. `.env.example`
> Ensure `.env.example` contains the names of every environment variable a fresh user needs, but contains placeholder/example values only—never real credentials.
> It should correspond to the environment variables the actual final application reads.
> 5. `requirements.txt` and frontend dependencies
> Verify that `requirements.txt` contains the backend dependencies actually required by the finished project, including PydanticAI and the dependencies needed for FastAPI/Portkey/database/application behavior.
> Verify that the frontend `package.json` and lockfile accurately contain the dependencies needed by the final frontend.
> Do not add unused libraries merely for appearance.
> 6. README
> Create or finalize `README.md` so a grader opening the repository can understand what the project is and how to run it.
> Include:
>
> * a concise description of the Campus Customs AI storefront;
> * its major features;
> * the technology stack;
> * prerequisites;
> * setup/install instructions;
> * environment-variable setup using `.env.example`;
> * exact backend and frontend run commands;
> * the expected backend/frontend ports;
> * an explanation that `data/campus_customs.db` and the supplied product images are intentionally excluded from the public repository;
> * any required local data setup needed to run the application with the course-provided database/images;
> * a brief description of the major `output/` artifacts.
>
> Make the README's commands match the commands already verified in `output/harness.md`. Do not introduce conflicting run instructions.
> 7. Preserve required evidence
> Make sure `output/app_check.html` still uses relative paths to `output/app_check_images/` and all referenced screenshots are included in the repository.
> Verify that the HTML report still renders correctly from the repository structure.
> Preserve `output/audit_trail.json` as required evidence. Do not rewrite its earlier records merely to make them prettier.
> 8. Full Problems 1–13 rubric audit
> Before publishing, audit the final project problem by problem against the requirements we implemented throughout Homework 4.
> In particular verify:
>
> * Problem 1: `AI_prompts.md` contains the required problem sections, actual prompts, and follow-up explanations where follow-ups were needed;
> * Problem 2: database/schema understanding and `output/harness.md`;
> * Problem 3: React + Vite + TypeScript storefront, reusable product components, and single-product view;
> * Problem 4: secure signup/login/session behavior using the existing users table;
> * Problem 5: the required backend structure, PydanticAI Agent rather than a hand-written model/tool loop, system prompt file, Portkey configuration, `gpt-5.6-luna`, and frontend chat widget;
> * Problem 6: real read-only database tools for search, product details/description/price, and inventory; all tools actually registered on the PydanticAI agent; required model-field explanations in the harness;
> * Problem 7: structured dynamic chatbot product results rendered as clickable product cards using the existing product-view behavior;
> * Problem 8: authenticated identity, isolated persistent history, guest behavior, and validated current-product context;
> * Problem 9: exactly two frontend and exactly two agent/backend usability improvements, with exactly those four documented in `output/usability.md`;
> * Problem 10: creative storefront styling and `output/design.md`;
> * Problem 11: actual-browser application testing, `output/app_check.html`, and screenshot evidence under `output/app_check_images/` for inventory lookup, dynamic search cards, and a Problem 9 usability feature;
> * Problem 12: append-only `output/audit_trail.json`, explicit safety rules, actual PydanticAI execution limits, result limits, and completed `output/harness.md` with models, tools, safety, limits, and verified run instructions;
> * Problem 13: public GitHub repository with the required project structure and no prohibited data/secrets.
>
> Do not treat functionally equivalent substitutions as satisfying an explicit technical requirement. Verify literal frameworks, filenames, paths, commands, arguments, models, and output files from the actual code/files.
> If you find a discrepancy, stop and tell me exactly what it is before silently changing a major architectural requirement. Small documentation, `.gitignore`, dependency, README, or obvious submission-preparation fixes may be made and reported.
> 9. Fresh-checkout verification
> Before publishing, test the repository contents as close as practical to a fresh clone:
>
> * no existing `.venv`;
> * no existing `node_modules`;
> * no real `.env`;
> * no generated catalogue/product copies unless the application intentionally regenerates them;
> * install from the committed dependency files;
> * verify the backend and frontend can start using the documented commands;
> * verify the application fails safely when required secrets are absent.
>
> Because the course database and product images are intentionally excluded from GitHub, distinguish failures caused by those intentionally absent course-provided assets from actual repository/setup errors.
> 10. Git verification before publishing
> Before any push, show me a concise summary of:
>
> * the files/directories that will be committed;
> * confirmation that the database and `data/products/` are not tracked;
> * confirmation that `.env` is not tracked;
> * confirmation that no secret was found in the commit contents;
> * the results of the Problems 1–13 audit;
> * the fresh-checkout test;
> * any remaining concerns.
>
> If you have the ability to create/push the GitHub repository from my environment, do not make it public or push it until the above checks pass. If authentication or an external action requires my approval/login, stop at that point and tell me exactly what I need to do.
> After the checks pass, create/publish the repository as required and verify the repository is actually public and accessible.
> 11. Prompt log
> Update `AI_prompts.md` with:
> `Problem 13: Final GitHub submission`
> Record this prompt exactly as I gave it to you.
> Keep all work inside `hw4`.
> At the end, give me:
>
> * the Problems 1–13 audit results;
> * the final repository file-tree summary;
> * the secret/privacy scan result;
> * confirmation of every specifically excluded file/directory;
> * the fresh-checkout result;
> * any changes made during the final audit;
> * the exact public GitHub repository URL, if publishing succeeded.

> Before publishing, please make two final changes.
>
> 1. Remove the course-provided test login credentials from the public README and AI_prompts.md, replacing them with a statement that test credentials are supplied separately with the course materials. Preserve the prompt log's structure and explain any necessary redaction rather than silently deleting an entire prompt.
> 2. Confirm whether the assignment's requirement to put code in a folder named `hw4` is satisfied by a GitHub repository named `hw4` with the project files at the repository root, or whether it explicitly requires an `hw4/` subdirectory. Do not guess. Tell me the exact relevant wording you have available and recommend the safest layout.
>
> After making the documentation changes, rerun the staged-content privacy scan and confirm that the local commit includes the changes.
> Do not push or publish yet. Report the results and wait for my approval.

The first submission prep left the course-provided test login in the public README and harness, so this follow-up had them replaced with a note that credentials are supplied separately (AI_prompts.md never contained them, so no prompt needed redaction) and asked to confirm the required repository layout before publishing.

> Approved. Please use the top-level hw4/ subdirectory layout and name the public GitHub repository shayajannati/hw4.
> Keep the existing local working project intact. Prepare the publication branch so the public repository contains an hw4/ directory with the required project files inside it.
> Before pushing, verify that:
>
> * All required files are under hw4/.
> * The database, product images, secrets, .env, generated files, and local environments remain excluded.
> * The published Git history contains no credentials.
> * The privacy scan passes for the exact commit being pushed.
> * The README instructions work from the new repository layout, including changing into hw4/ before running commands.
> * The Problem 11 HTML report still finds all 10 screenshots.
> * The complete Problems 1–13 audit remains passing.
>
> If everything passes, create the public repository, push the verified branch as main, and confirm that GitHub shows the expected hw4/ directory and that the repository is publicly accessible.
> Finally, give me the exact public repository URL, the final commit hash, and the results of your post-push verification. Log this follow-up under Problem 13 in AI_prompts.md.

The assignment's "folder named hw4" wording didn't say whether hw4/ is the repository root or a subdirectory, so this follow-up chose the safer layout (a top-level hw4/ directory in the public repository shayajannati/hw4) and set the pre- and post-publication checks.
