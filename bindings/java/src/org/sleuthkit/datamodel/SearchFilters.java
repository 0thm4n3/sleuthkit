/*
 * Autopsy Forensic Browser
 * 
 * Copyright 2011 Basis Technology Corp.
 * Contact: carrier <at> sleuthkit <dot> org
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 * 
 *     http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.sleuthkit.datamodel;

import java.util.Arrays;
import java.util.List;

/**
 * Filters database results by file extension.
 */
public class SearchFilters implements DisplayableItem{

    SleuthkitCase skCase;

    public enum FileSearchFilter implements DisplayableItem {
        TSK_IMAGE_FILTER(0, "TSK_IMAGE_FILTER", "Images", Arrays.asList(".jpg", ".jpeg", ".png", ".psd", ".nef")),
        TSK_VIDEO_FILTER(1, "TSK_VIDEO_FILTER", "Videos", Arrays.asList(".mov", ".avi", ".m4v")),
        TSK_AUDIO_FILTER(2, "TSK_AUDIO_FILTER", "Audio", Arrays.asList(".mp3", ".aac", ".wav", ".ogg", ".wma", ".m4a")),
        TSK_DOCUMENT_FILTER(3, "TSK_DOCUMENT_FILTER", "Documents", Arrays.asList(".doc", ".docx", ".pdf", ".xls")),
        TSK_APPLICATION_FILTER(4, "TSK_APPLICATION_FILTER", "Applications", Arrays.asList(".exe"));

        int id;
        String name;
        String displayName;
        List<String> filter;

        private FileSearchFilter(int id, String name, String displayName, List<String> filter){
            this.id = id;
            this.name = name;
            this.displayName = displayName;
            this.filter = filter;
        }

        @Override
        public <T> T accept(DisplayableItemVisitor<T> v) {
            return v.visit(this);
        }

        @Override
        public boolean isOnto() {
            return false;
        }

        public String getName(){
            return this.name;
        }

        public int getId(){
            return this.id;
        }

        public String getDisplayName(){
            return this.displayName;
        }

        public List<String> getFilter(){
            return this.filter;
        }
    }

    public SearchFilters(SleuthkitCase skCase){
        this.skCase = skCase;
    }

    @Override
    public <T> T accept(DisplayableItemVisitor<T> v) {
        return v.visit(this);
    }

    @Override
    public boolean isOnto() {
        return false;
    }

    public SleuthkitCase getSleuthkitCase(){
        return this.skCase;
    }
}
